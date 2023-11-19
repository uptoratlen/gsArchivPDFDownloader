__version_info__ = ('0', '8', '2')
__version__ = '.'.join(__version_info__)

import argparse
import glob
import re
import shutil
from datetime import datetime
import json
import os
import sys
from time import sleep, time
import tempfile

import ghostscript
from win32 import win32print

import logging
from logging.handlers import RotatingFileHandler

#from get_gecko_driver import GetGeckoDriver

from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.options import Options as Options_FF
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException



def _open_gs_and_login(_url, _user, _password, _options, _profile):
    """Returns a webdriver :class:'selenium.webdriver.firefox.webdriver.WebDriver' object
    Will open a browser with options and profile given,
    login to page with user and password

    Args:
        _url (str): URL of startpage to login
        _user (str): Username from credentials
        _password (str): Password from credentials
        _options (class): Firefox options
        _profile (class): Firefox profile

    Returns:
        class: webdriver

    """
    # open browser and login
    _driver = webdriver.Firefox(options=_options, firefox_profile=_profile)
    _wait = WebDriverWait(_driver, 20)
    _driver.get(_url)
    logging.info(f"Browser now started with URL:{_url} - "
                 f"try now to log in with user/password [xxx/***]")
    _wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR,'button.btn:nth-child(8)')))
    sleep(2)
    _driver.find_element_by_id('page-login-inp-username').send_keys(_user)
    sleep(2)
    _driver.find_element_by_id('page-login-inp-password').send_keys(_password)
    _driver.find_element_by_css_selector('button.btn:nth-child(8)').click()
    return _driver


def _hlp_display_type(varx):
    """

    Args:
        varx:

    Returns:

    """
    print(f"{varx} if of type {type(varx)}")
    return True


def json_config_check(_json_config, _key_list):
    """Checks if read json file contais all requeired keys
    exists when check is ngeativ (key is missing)

    Args:
        _json_config (dict): the json dict to check
        _key_list (list): A list of given key names for checking

    Returns:
        bool: True if all is ok
    """
    logging.info(f'Checking json config')
    logging.debug(f'{_json_config}')
    for key_check in _key_list:
        if key_check not in _json_config.keys():
            logging.error(f"Json file looks incomplete - key:'{key_check}' is missing")
            sys.exit(99)
    return True


def filename_modification(filestring_downloaded, filestring_whiledownloaded, filestring_target, edition_month,
                          edition_jahr, edition2d="no"):
    """Filenames must be altered according to the server/download and local/target definition in json file

    Args:
        filestring_downloaded (str): The filename string from json file for the download name
        filestring_whiledownloaded (str): The filename string from json file for the download name while downloading
        filestring_target (str): The filename string from json file for the target/local name
        edition_month (str):  The edition number aka month as string
        edition_jahr (str): The edition year aka jahr as string
        edition2d (str, optional): yes will pad always 0 to the 1-9 editions

    Returns:
        (tuple): tuple containing:
             filestring_downloaded (str): the final name of the file used in the download url
             filestring_whiledownloaded (str): the final name of the file used in the download url while downloading
             filestring_target (str): the final name of the file used in the target folder
    Raises:
        TypeError: in case input is not str and exists
    """
    logging.debug(f'Filename after Download on disk :[{filestring_downloaded}]')
    logging.debug(f'Filename while Download on disk :[{filestring_whiledownloaded}]')
    logging.debug(f'Filename for Target(modified)   :[{filestring_target}]')
    try:
        if edition2d.lower() == 'yes':
            for filenamerepl in (("<ausgabe>", f"{'{:0>2}'.format(edition_month)}"), ("<jahr>", edition_jahr)):
                filestring_target = filestring_target.replace(*filenamerepl)
        else:
            for filenamerepl in (("<ausgabe>", edition_month.lstrip('0')), ("<jahr>", edition_jahr)):
                filestring_target = filestring_target.replace(*filenamerepl)

        for filenamerepl in (("<ausgabe>", edition_month.lstrip('0')), ("<jahr>", edition_jahr)):
            filestring_downloaded = filestring_downloaded.replace(*filenamerepl)
            filestring_whiledownloaded = filestring_whiledownloaded.replace(*filenamerepl)

        logging.info(f'Filename after Download on disk :[{filestring_downloaded}]')
        logging.info(f'Filename while Download on disk :[{filestring_whiledownloaded}]')
        logging.info(f'Filename for Target(modified)   :[{filestring_target}]')
        return filestring_downloaded, filestring_whiledownloaded, filestring_target
    except TypeError as _e:
        logging.exception(f'TypeError Exception Raised - str expected int found -{_e}')
        sys.exit(99)
    except (ValueError, AttributeError) as _e:
        logging.exception(f'ValueError/AttributeError Exception Raised - {_e}')
        sys.exit(99)


def download_range(_range_start_year, _range_start_month, _range_end_year, _range_end_month):
    """Download wrapper for range and full

    Args:
        _range_start_year (str): year of requested downloads start
        _range_start_month (str): month/edition of requested downloads start
        _range_end_year (str): year of requested downloads end
        _range_end_month (str): month/edition of requested downloads end

    Returns:
        None

    """
    _jahr = _range_start_year
    _ausgabe = _range_start_month
    _continue_download = True
    error_list = []
    _abort_flag = 0
    while _continue_download:
        logging.info(f"Trying now to download  (Edition/Year) => ({_ausgabe}/{_jahr})")
        _result = download_edition(int(_jahr), int(_ausgabe),
                                   user_data[0]['filenamepattern_fromserver'],
                                   user_data[0]['filenamepattern_fromserverwhiledl'],
                                   user_data[0]['filenamepattern_intarget'], user_data[0]['skip_editions'])
        if _result < 10:
            _abort_flag = 0
        else:
            logging.warning(f'Download failed(load) - adding [{_ausgabe}/{_jahr}] to report.')
            error_list.append(f'{_jahr}/{_ausgabe}')
            _abort_flag += 1
            logging.info(f"As edition was not found; increase abort counter "
                         f"[{_abort_flag}/{user_data[0]['abortlimit']}]")

        if _abort_flag >= user_data[0]['abortlimit']:
            logging.info(f'The abort limitcounter reached the maxmium allwed and will now abort the run')
            break

        _ausgabe = str(int(_ausgabe) + 1)
        if int(_jahr) == 2013 and int(_ausgabe) == 13:
            logging.info('Special year 2013 with 13th edition in range')
        elif (int(_jahr) != 2013 and int(_ausgabe) == 13) or (int(_jahr) == 2013 and int(_ausgabe) == 14):
            logging.info('Roll over in loop to next year')
            _ausgabe = str(1)
            _jahr = str(int(_jahr) + 1)

        if int(_range_end_year + _range_end_month.zfill(2)) >= int(_jahr + _ausgabe.zfill(2)):
            logging.debug('Loop fine - expecting still a next edition.')
            continue
        else:
            logging.debug('Stop latest download loop - max reached.')
            if len(error_list) > 0:
                logging.warning(f'Some edition showed some recoverable issues while downloading -'
                                f' try same run a second time.')
                logging.warning(f'{error_list}')
            _continue_download = False


def download_cover(_jahr, _monat):
    """The cover download function

    Args:
        _jahr (int): year of requested cover
        _monat (int): month/edition of requested cover

    Returns:
        dl_state (int): flag for return value
        0 = ok
        1 = skipped
        2 = existing
        3 = before 1997/08
        10 = failed to download
        11 = failed to move

    """
    filename_cover_intarget_sub = f'GS{_jahr}_{str(_monat).zfill(2)}_Inlay-Coverpack'

    if os.path.exists(f"{user_data[0]['downloadtargetcovers']}/{jahr}/"
                      f"{filename_cover_intarget_sub}.pdf"):
        logging.info("Skip, download of cover - already existing in target")
        return 2

    files = glob.glob(f"{user_data[0]['downloadtargetcovers']}/*.pdf*")
    for fn in files:
        logging.debug(f"File from previous run found - remove [{fn}]")
        os.remove(fn)
    logging.debug(f"Previous files found, count = {format(len(files))}, removed")
    try:
        logging.info(f'https://www.gamestar.de/dvdhuelle{str(_monat).zfill(2)}{_jahr}')
        driver.get(f'https://www.gamestar.de/dvdhuelle{str(_monat).zfill(2)}{_jahr}')
    except TimeoutException as e:
        logging.info("Expected timeout - caused by selenium pdf download")
        pass
    except Exception as e:
        logging.error(e)
        pass
    logging.info("Check for newest file...")
    list_of_files = glob.glob(f"{user_data[0]['downloadtargetcovers']}/*pdf", recursive=False)
    newest_file = max(list_of_files, key=os.path.getctime)
    logging.debug(f"Newest file (assuming downloaded):{newest_file}")
    if ".pdf" not in newest_file:
        logging.warning(f"It looks like this cover is missing on server:[{str(_monat).zfill(2)}{_jahr}]")
        return 10

    if not os.path.exists(f"{user_data[0]['downloadtargetcovers']}/{_jahr}"):
        logging.info(f"Create folder {user_data[0]['downloadtargetcovers']}/{_jahr}")
        os.makedirs(f"{user_data[0]['downloadtargetcovers']}/{_jahr}")

    result_cover = wait_for_download(f"{newest_file}", timeout=10)
    logging.info(f"Move now file[{newest_file}] to target[{user_data[0]['downloadtargetcovers']}/"
                 f"{_jahr}/{filename_cover_intarget_sub}.pdf]")
    shutil.move(f"{newest_file}", f"{user_data[0]['downloadtargetcovers']}/{_jahr}/"
                                  f"{filename_cover_intarget_sub}.pdf")
    return 0


def download_edition(jahrdl, ausgabedl, _filestring_download, _filestring_whiledownload,
                     _filestring_target, _skip_editions):
    """The main download function

    Args:
        jahrdl (int): year of requested downloads
        ausgabedl (int): month/edition of requested downloads
        _filestring_download (str): The filename string from json file for the download name
        _filestring_whiledownload (str): The filename string from json file for the download name while downloading
        _filestring_target (str): The filename string from json file for the target/local name
        _skip_editions (dict): dict of all special editions that should be skipped as they are
         expected to cause a issue (server side error)

    Returns:
        dl_state (int): flag for return value
        0 = ok
        1 = skipped
        2 = existing
        3 = before 1997/08
        10 = failed to download
        11 = failed to move
        12 = page load failed

    """
    wait_de = WebDriverWait(driver, 10)

    _filenamepattern_download, _filenamepattern_whiledownload, _filenamepattern_local = filename_modification(
        _filestring_download, _filestring_whiledownload, _filestring_target, str(ausgabedl),
        str(jahrdl), user_data[0]['edition2d'])
    skip_download = False

    try:
        for _editions in _skip_editions:
            for _year in _editions:
                if not str(jahrdl) in _year:
                    raise StopIteration
                else:

                    if str(ausgabedl) in _editions[_year].split(','):
                        logging.warning(f"The requested edition [{ausgabedl}/{jahrdl}] is a marked-for-skip edition")
                        logging.warning(f"No download will be initiated. "
                                        f"Edit gs.json to add or remove editions from skip list.")
                        skip_download = True
    except StopIteration:
        # continue as not in skip list
        pass

    if skip_download:
        return 1

    if jahrdl == 1997 and ausgabedl <= 8:
        logging.info(f"Skip download - First edition of 1997 is 9 "
                     f"'requested ({ausgabedl}/{jahrdl}'")
        return 3
    if os.path.exists(f"{user_data[0]['downloadtarget']}/{jahrdl}/{_filenamepattern_local}"):
        logging.info(f"Skip download - already existing "
                     f"'{user_data[0]['downloadtarget']}/{jahrdl}/{_filenamepattern_local}'")
        return 2
    try:
        logging.info(f'Try now download of : Jahr {jahrdl} and Ausgabe {ausgabedl} '
                     f'- URL:https://www.gamestar.de/_misc/plus/showbk.cfm?bky={jahrdl}&bkm={ausgabedl}')
        # open url of blätterkatalog
        driver.get(f'https://www.gamestar.de/_misc/plus/showbk.cfm?bky={jahrdl}&bkm={ausgabedl}')
        sleep(4)
        try:
            driver.find_element_by_css_selector('#cbutton1').click()
        except:
            logging.info('Cookies already satisfied')
        sleep(3)

        filesdl = glob.glob(f"{user_data[0]['downloadtarget']}/*.pdf*")
        for fndl in filesdl:
            logging.debug(f"File from previous run found - remove [{fndl}]")
            os.remove(fndl)
        logging.info(f"Previous files found, count = {format(len(filesdl))}, removed")
        sleep(5)

        try:
            # wait for the save button on the right side
            save_button = wait_de.until(ec.visibility_of_element_located((By.XPATH,
                                                                          '//*[@id="top_menu_save"]')))
        except TimeoutException:
            logging.warning('Looks like the page not found is displayed - this edition failed')
            return 10
        # navigate to the button; click only did not work as expected
        ActionChains(driver).move_to_element(save_button).click().perform()
        # wait for titel to apear; used as a confirm that the editon is fully loaded
        wait_de.until(ec.visibility_of_element_located((By.XPATH, '//p[@class="title"]')))
        # wait for the complete.pdf; check if the user is a valid user  and not guest
        wait_de.until(ec.visibility_of_element_located((By.XPATH, "//a[contains(@href, 'complete.pdf')]")))
        # click on the download / save button
        driver.find_element_by_xpath("//a[contains(@href, 'complete.pdf')]").click()
        sleep(1)
        resultdl1 = wait_for_download(f"{user_data[0]['downloadtarget']}/{_filenamepattern_whiledownload}",
                                      timeout=user_data[0]['downloadtimeout'])
        if resultdl1 is True:
            dl_state = 0
            move_downloaded(f"{user_data[0]['downloadtarget']}", jahrdl,
                            _filenamepattern_download, _filenamepattern_local)
        else:
            dl_state = 11
            logging.warning(f'Download failed before move.')

    except TimeoutException as t:
        dl_state = 12
        logging.exception(f'Browser page load failed;maybe edition does not exist;or very slow load '
                          f'- timeout exception:{t}')

    except Exception as _e:
        logging.exception(f'Exception:{_e}')
        driver.quit()
        sys.exit(99)

    return dl_state


def wait_for_download(filedownloadfullpath, timeout=30):
    """Will check if a partial download still exists

    Args:
        filedownloadfullpath (str): the full download name of the target/downloaded file, absolute path
        timeout (int, optional): Timeout given for wait until no partial files are seen anymore

    Returns:
        The return value. True for Download is complete, no partial files seen,
         False for Partial donwloaded file still seen after timeout.

    """
    logging.debug(f'Download timeout is:[{timeout}] - looking for [{filedownloadfullpath}.part]')
    time_out = time() + 2

    while not glob.glob(f'{filedownloadfullpath}.part') and time() < time_out:
        logging.debug(f'{filedownloadfullpath}.part not yet seen- waiting for first download')
        sleep(2)
    time_out = time() + timeout
    while glob.glob(f'{filedownloadfullpath}.part') and time() < time_out:
        logging.debug(f'{filedownloadfullpath}.part Seen- waiting')
        sleep(1.5)
    if glob.glob(f'{filedownloadfullpath}.part'):
        logging.warning('Download still in progress - may need recheck - aborting wait to continue'
                        ' - may complete in background')
        return False
    else:
        logging.info('Download done successful')
        return True


def move_downloaded(_targetfolder, _year, _fn_downloaded, _fn_target, _timeout=30):
    """Will check if a partial download still exists

    Args:
    _targetfolder (str): absolute path of target folder no trailing path separator
    _year (int): year; will be used as a subfolder
    _fn_downloaded (str): the name of the downloaded file
    _fn_target (str): the name of the file in the target folder
    _timeout (int): a grace time for seeing the file on the disk

    Returns:
        bool: True if no error detected, False if a error occurred while moving file

    """

    logging.info(f'Trying now to move the downloaded file with a _timeout of:[{_timeout}]')
    if not os.path.exists(f"{_targetfolder}/{_year}"):
        logging.info(f"Create folder [{_targetfolder}/{_year}]")
        os.makedirs(f"{_targetfolder}/{_year}")

    time_out = time() + _timeout
    while not os.path.exists(f'{_targetfolder}/{_fn_downloaded}') and time() < time_out:
        logging.info(f'Downloaded file [{_targetfolder}/{_fn_downloaded}] still not seen- waiting')
        sleep(1.5)
    if os.path.exists(f'{_targetfolder}/{_fn_downloaded}'):
        shutil.move(f'{_targetfolder}/{_fn_downloaded}',
                    f'{_targetfolder}/{_year}/{_fn_target}')
        logging.info('Move Download done successful')
        return True
    else:
        logging.warning(f'Move not performed as file [{_targetfolder}/{_fn_downloaded}] is not seen.')
        return False


def print_cover(cover_file, page_to_print):
    """Extracts a given page number from the inlay file and than print the file to the default printer
    the extract was added as direct print was not working in the expected way

    Args:
    cover_file (str): absolute path of input inlay pdf file
    page_to_print (int): the page of the inlay to be printed

    Returns:
        none
    """
    temp1 = tempfile.mktemp('.eps')
    page_seite = str(page_to_print)
    args_extract = [
        "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dNOPROMPT",
        "-q",
        "-sDEVICE=eps2write",
        "-dFirstPage="+page_seite,
        "-dLastPage="+page_seite,
        "-sOutputFile=" + temp1,
        "-f",
        cover_file
    ]
    # for printing on default printer
    args_printing = [
        "-dPrinted", "-dBATCH", "-dNOPAUSE", "-dSAFER", "-dNOPROMPT", "-dQueryUser=3",
        "-q",
        "-dNumCopies=1",
        "-dEPSFitPage",
        "-sDEVICE=mswinpr2",
        f'-sOutputFile="%printer%{win32print.GetDefaultPrinter()}"',
        "-f",
        temp1
    ]
    logging.info(f"Create temp PDF file [{temp1}]")
    ghostscript.Ghostscript(*args_extract)
    logging.info(f"Print to Printer:{win32print.GetDefaultPrinter()}")
    ghostscript.Ghostscript(*args_printing)
    os.remove(temp1)


if __name__ == '__main__':
    #get_driver = GetGeckoDriver()
    #get_driver.install()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    key_list_gsjson = ['log_level', 'downloadtarget', 'edition2d', 'downloadtimeout', 'abortlimit',
                       'filenamepattern_intarget', 'filenamepattern_fromserver', 'filenamepattern_fromserver',
                       'latestdownload', 'browser_display_on_latest', 'skip_editions']

    # read config from json file
    json_config_file = 'gs.json'
    if not os.path.exists(json_config_file):
        logging.error(f'Sorry, but config file [{json_config_file}] was not found in dir.')
        sys.exit(96)
    with open(json_config_file, 'r') as file:
        user_data = json.loads(file.read())

    # read credentials from json
    json_credential_file = 'gs_credential.json'
    if not os.path.exists(json_credential_file):
        logging.error(f'Sorry, but credential file [{json_credential_file}] was not found in dir.')
        sys.exit(96)
    with open(json_credential_file, 'r') as file:
        user_credential = json.loads(file.read())

    # Loggin set up
    LOG_FILE = os.path.dirname(os.path.abspath(__file__)) + '/gsArchivPDFDownloader.log'
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=10)
    sh = logging.StreamHandler(sys.stdout)
    loglvl_allowed = ['debug', 'info', 'warning', 'error', 'critical']

    log_level = logging.getLevelName('DEBUG')
    if user_data[0]['log_level'].lower() in loglvl_allowed:
        log_level = logging.getLevelName(user_data[0]['log_level'].upper())
    else:
        logging.debug("Switch back to Debug Level as user used a unexpected value in log level")
    logger.setLevel(log_level)

    if log_level == 10:
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - [%(name)s.%(funcName)s:%(lineno)d] '
                                      '- %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    else:
        formatter = logging.Formatter('%(asctime)s:[%(levelname)-5.5s] %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

    parser = argparse.ArgumentParser(description='Download GameStar PDFs from webpage')
    parser.add_argument('-l', '--latest',  action='store_const',
                        const=True, help=f"try to download always the newest (starting from "
                                         f"{user_data[0]['latestdownload'][0]['year']}-"
                                         f"{user_data[0]['latestdownload'][0]['edition']})")
    parser.add_argument('-cl', '--coverlatest',  action='store_const',
                        const=True, help=f"try to download always the newest cover (starting from "
                                         f"{user_data[0]['latestdownload_cover'][0]['year']}-"
                                         f"{user_data[0]['latestdownload_cover'][0]['edition']})")
    parser.add_argument('-f', '--full',  action='store_const',
                        const=True, help=f"a full download of all editions from 1997/09 to "
                                         f"{datetime.now().month}/"
                                         f"{datetime.now().year}")
    parser.add_argument('-c', '--cover',  action='store_const',
                        const=True, help=f"a full download of all covers from from 2000/01 to "
                                         f"{datetime.now().month}/"
                                         f"{datetime.now().year}")
    parser.add_argument('-y', '--year', type=int, help='a single year in range [1997-2035]')
    parser.add_argument('-r', '--range', type=str, help='a range in format yyyy:mm-yyyy:mm; example -r 2019:09-2020:11')
    parser.add_argument('-v', '--version', action='version', version="%(prog)s ("+__version__+")")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()

    if args.year and (args.year < 1997 or args.year > 2035):
        parser.error("Select a year within range 1997 to 2035")
    if args.range:
        matched = re.match(r"^(199[7-9]|20[0-3]\d):(0[0-9]|1[0123])-(199[7-9]|20[0-3]\d):(0[0-9]|1[0123])$", args.range)
        if not bool(matched):
            logging.error('The range argument is not in the right format.')
            sys.exit(95)

    logging.info(f"gsArchivPDFDownloader Version:{__version__}")
    # Precheck
    json_config_check(user_data[0], key_list_gsjson)
    for x in [user_credential[0]['user'], user_credential[0]['password']]:
        if 'edit_your_' in x:
            logging.error(f"Sorry, you forget to edit the gs_credential.json - "
                          f"it still contains the dummy user/password "
                          f"[{user_credential[0]['user']}/{user_credential[0]['password']}].")
            sys.exit(98)

    if not os.path.exists(f"{user_data[0]['downloadtarget']}"):
        logging.info(f"Create folder [{user_data[0]['downloadtarget']}]")
        os.makedirs(f"{user_data[0]['downloadtarget']}")

    profileFF: FirefoxProfile = webdriver.FirefoxProfile()
    profileFF.set_preference('browser.download.folderList', 2)
    profileFF.set_preference('browser.helperApps.alwaysAsk.force', False)
    profileFF.set_preference('browser.download.manager.showWhenStarting', False)
    profileFF.set_preference('browser.download.dir', f"{user_data[0]['downloadtarget']}")

    profileFF.set_preference('plugin.disable_full_page_plugin_for_types', 'application/pdf')
    profileFF.set_preference('pdfjs.disabled', True)
    profileFF.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')

    optionsFF = Options_FF()
    optionsFF.headless = False
    if args.latest and user_data[0]['browser_display_on_latest'].lower() == "no":
        optionsFF.headless = True

    logging.info(f"Download location:{user_data[0]['downloadtarget']}")
    logging.info(f"filenamepattern_fromserver:{user_data[0]['filenamepattern_fromserver']}")
    logging.info(f"filenamepattern_fromserverwhiledl:{user_data[0]['filenamepattern_fromserverwhiledl']}")
    logging.info(f"filenamepattern_intarget  :{user_data[0]['filenamepattern_intarget']}")

    url_login = 'https://www.gamestar.de/login/'
    url = 'https://www.gamestar.de/plus/'

    if args.year:
        logging.info('Run Type: Year')
        driver = _open_gs_and_login(url_login, user_credential[0]['user'], user_credential[0]['password'],
                                    optionsFF, profileFF)
        year = args.year
        abort_flag = 0
        for edition in range(1, 14):
            result = download_edition(int(year), edition, user_data[0]['filenamepattern_fromserver'],
                                      user_data[0]['filenamepattern_fromserverwhiledl'],
                                      user_data[0]['filenamepattern_intarget'], user_data[0]['skip_editions'])
            if result < 10:
                abort_flag = 0
            else:
                abort_flag += 1
                logging.info(f"As edition was not found; increase abort counter "
                             f"[{abort_flag}/{user_data[0]['abortlimit']}]")

            if abort_flag >= user_data[0]['abortlimit']:
                logging.info(f'The abort limitcounter reached the maxmium allwed and will now abort the run')
                break

    elif args.latest:
        logging.info('Run Type: Latest')
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_day = datetime.now().day
        max_year_latest = datetime.now().year
        max_month_latest = datetime.now().month

        jahr = user_data[0]['latestdownload'][0]['year']
        ausgabe = user_data[0]['latestdownload'][0]['edition']
        jahr_lastdl = jahr
        ausgabe_lastdl = ausgabe

        if int(ausgabe) == 12:
            logging.debug('Latest downloaded edition was a 12, rollover to next year.')
            jahr = str(int(jahr) + 1)
            ausgabe = str(0)
            max_month_latest = 1
        else:
            if current_day > 15:
                logging.debug('Later than 15th so try also a next month edition.')
                max_month_latest = max_month_latest + 1

        ausgabe = str(int(ausgabe)+1)
        continue_download = True
        driver = _open_gs_and_login(url_login, user_credential[0]['user'], user_credential[0]['password'],
                                    optionsFF, profileFF)
        while continue_download:
            logging.info(f"Trying now to download the latest version for (Editions/Year) (curMonth/curYear)=>"
                         f"({ausgabe}/{jahr}) ({current_month}/{current_year})")
            logging.debug(f"maxMonth, maxYear=>({max_month_latest}, {max_year_latest})")

            result = download_edition(int(jahr), int(ausgabe),
                                      user_data[0]['filenamepattern_fromserver'],
                                      user_data[0]['filenamepattern_fromserverwhiledl'],
                                      user_data[0]['filenamepattern_intarget'], user_data[0]['skip_editions'])
            logging.debug(f"result [{result}]")
            if result < 10:
                logging.debug(f"Last success download [{ausgabe_lastdl}/{jahr_lastdl}]")
                jahr_lastdl = jahr
                ausgabe_lastdl = ausgabe

            ausgabe = str(int(ausgabe)+1)
            if int(ausgabe) == 13:
                logging.debug('Roll over in loop to next year')
                ausgabe = str(1)
                jahr = str(int(jahr)+1)
                if int(jahr) > max_year_latest:
                    logging.debug(f'Too far in future({jahr})')
                    break

            if int(str(max_year_latest) + str(max_month_latest).zfill(2)) >= int(str(jahr) + str(ausgabe).zfill(2)):
                logging.debug('Loop fine - expecting still a next edition.')
                continue
            else:
                logging.debug('Stop latest download loop - max reached.')
                continue_download = False

        logging.info(f"Last success download [{ausgabe_lastdl}/{jahr_lastdl}]")
        user_data[0]['latestdownload'][0]['year'] = jahr_lastdl
        user_data[0]['latestdownload'][0]['edition'] = ausgabe_lastdl

        logging.info(f'Update JSON file ({json_config_file})')
        with open(json_config_file, 'w') as outfile:
            json.dump(user_data, outfile, indent=4, sort_keys=False)
    elif args.full:
        logging.info('Run Type: Full')
        range_start_year = "1997"
        range_start_month = "09"
        range_end_year = str(datetime.now().year)
        range_end_month = str(datetime.now().month)

        logging.debug(f"The range is from {range_start_month}/{range_start_year} to {range_end_month}/{range_end_year}")
        driver = _open_gs_and_login(url_login, user_credential[0]['user'], user_credential[0]['password'],
                                    optionsFF, profileFF)
        download_range(range_start_year, range_start_month, range_end_year, range_end_month)

    elif args.range:
        logging.info('Run Type: Range')
        range_selection = args.range

        range_selection_split = range_selection.split("-")
        range_start_year = range_selection_split[0].split(":")[0]
        range_start_month = range_selection_split[0].split(":")[1]
        range_end_year = range_selection_split[1].split(":")[0]
        range_end_month = range_selection_split[1].split(":")[1]

        logging.debug(f"The range is from {range_start_month}/{range_start_year} to {range_end_month}/{range_end_year}")
        if int(range_start_year + range_start_month.zfill(2)) <= 199708:
            logging.error('Range start is to early.')
            sys.exit(95)
        if int(range_start_year + range_start_month.zfill(2)) > int(range_end_year + range_end_month.zfill(2)):
            logging.error('Range end is older than start.')
            sys.exit(95)
        driver = _open_gs_and_login(url_login, user_credential[0]['user'], user_credential[0]['password'],
                                    optionsFF, profileFF)
        download_range(range_start_year, range_start_month, range_end_year, range_end_month)
    elif args.cover:
        logging.info('Run Type: Covers (full)')
        profileFF.set_preference('browser.download.dir', f"{user_data[0]['downloadtargetcovers']}")
        optionsFF.headless = False
        if user_data[0]['browser_display_on_latest'].lower() == "no":
            optionsFF.headless = True
        driver = webdriver.Firefox(options=optionsFF, firefox_profile=profileFF)
        driver.set_page_load_timeout(1)
        wait = WebDriverWait(driver, 5)
        if not os.path.exists(f"{user_data[0]['downloadtargetcovers']}"):
            logging.info(f"Create folder {user_data[0]['downloadtargetcovers']}")
            os.makedirs(f"{user_data[0]['downloadtargetcovers']}")

        try:
            for jahr in range(2000, datetime.now().year+1):
                for monat in range(1, 13):
                    download_cover(jahr, monat)
        except Exception as e:
            logging.error(e)
            pass
    elif args.coverlatest:
        logging.info('Run Type: Covers (latest)')
        profileFF.set_preference('browser.download.dir', f"{user_data[0]['downloadtargetcovers']}")
        optionsFF.headless = False
        if user_data[0]['browser_display_on_latest'].lower() == "no":
            optionsFF.headless = True
        driver = webdriver.Firefox(options=optionsFF, firefox_profile=profileFF)
        driver.set_page_load_timeout(1)
        wait = WebDriverWait(driver, 5)
        if not os.path.exists(f"{user_data[0]['downloadtargetcovers']}"):
            logging.info(f"Create folder {user_data[0]['downloadtargetcovers']}")
            os.makedirs(f"{user_data[0]['downloadtargetcovers']}")

        logging.info('Run Type: CoverLatest')
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_day = datetime.now().day
        max_year_latest = datetime.now().year
        max_month_latest = datetime.now().month

        jahr = user_data[0]['latestdownload_cover'][0]['year']
        ausgabe = user_data[0]['latestdownload_cover'][0]['edition']
        jahr_lastdl = jahr
        ausgabe_lastdl = ausgabe

        if int(ausgabe) == 12:
            logging.debug('Latest downloaded cover was a 12, rollover to next year.')
            jahr = str(int(jahr) + 1)
            ausgabe = str(0)
            max_month_latest = 1
        else:
            if current_day > 15:
                logging.debug('Later than 15th so try also a next month cover.')
                max_month_latest = max_month_latest + 1

        ausgabe = str(int(ausgabe) + 1)
        continue_download = True

        while continue_download:
            logging.info(f"Trying now to download the latest cover for (Cover/Year) (curMonth/curYear)=>"
                         f"({ausgabe}/{jahr}) ({current_month}/{current_year})")
            logging.debug(f"maxMonth, maxYear=>({max_month_latest}, {max_year_latest})")

            result = download_cover(int(jahr), int(ausgabe))
            logging.debug(f"result [{result}]")

            if result < 10:
                logging.debug(f"Last success download [{ausgabe_lastdl}/{jahr_lastdl}]")
                jahr_lastdl = jahr
                ausgabe_lastdl = ausgabe
                if result == 0 and user_data[0]['cover_page_print'].lower() == "yes":
                    print_cover(f"{user_data[0]['downloadtargetcovers']}/{jahr}/GS{jahr}_{str(ausgabe).zfill(2)}_Inlay-Coverpack.pdf",
                                user_data[0]['cover_page_number'])

            ausgabe = str(int(ausgabe) + 1)
            if int(ausgabe) == 13:
                logging.debug('Roll over in loop to next year')
                ausgabe = str(1)
                jahr = str(int(jahr) + 1)
                if int(jahr) > max_year_latest:
                    logging.debug(f'Too far in future({jahr})')
                    break

            if int(str(max_year_latest) + str(max_month_latest).zfill(2)) >= int(str(jahr) + str(ausgabe).zfill(2)):
                logging.debug('Loop fine - expecting still a next cover.')
                continue
            else:
                logging.debug('Stop latest download loop - max reached.')
                continue_download = False

        logging.info(f"Last success download [{ausgabe_lastdl}/{jahr_lastdl}]")
        user_data[0]['latestdownload_cover'][0]['year'] = jahr_lastdl
        user_data[0]['latestdownload_cover'][0]['edition'] = ausgabe_lastdl

        logging.info(f'Update JSON file ({json_config_file})')
        with open(json_config_file, 'w') as outfile:
            json.dump(user_data, outfile, indent=4, sort_keys=False)

    else:
        logging.error('Run Type: not supported')
        sys.exit(97)

    logging.info(f"Last requested edition downloaded - give job some time (10s) to finish, for no good reason...")
    sleep(10)
    driver.quit()
    logging.info('Job done')
