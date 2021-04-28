import sys
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.options import Options as Options_FF
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

import os
import json

import argparse
from time import sleep, time


def filename_modification(filestring_download_in, filestring_local_in, edition_month, edition_jahr):
    filenamepattern_4download = filestring_download_in
    filenamepattern_4target = filestring_local_in

    if user_data[0]['edition2d'].lower() == 'yes':
        for filenamerepl in (("<ausgabe>", f"{edition_month:02d}"), ("<jahr>", str(edition_jahr))):
            filenamepattern_4target = filenamepattern_4target.replace(*filenamerepl)

    else:
        for filenamerepl in (("<ausgabe>", str(edition_month)), ("<jahr>", str(edition_jahr))):
            filenamepattern_4target = filenamepattern_4target.replace(*filenamerepl)

    for filenamerepl in (("<ausgabe>", str(edition_month)), ("<jahr>", str(edition_jahr))):
        filenamepattern_4download = filenamepattern_4download.replace(*filenamerepl)
    return filenamepattern_4download, filenamepattern_4target


def download_edition(jahr_start, ausgaben_start, jahr_end, ausgaben_end,
                     filestring_download, filestring_target):
    wait_de = WebDriverWait(driver, 10)
    dl_success = True
    for jahr in range(jahr_start, jahr_end+1):
        for ausgabe in range(ausgaben_start, ausgaben_end+1):
            filenamepattern_download, filenamepattern_local = filename_modification(
                filestring_target, filestring_download, ausgabe, jahr)

            logging.debug(f'Filepattern(from server)     :[{filenamepattern_download}]')
            logging.debug(f'Filepattern(local for target):[{filenamepattern_local}]')

            if jahr == 2017 and ausgabe == 10:
                logging.info(f"Warning - this is the current (by 11 March 2021) faulty download link of "
                             f"'{user_data[0]['downloadtarget']}/{jahr}/{filenamepattern_local}'")
                logging.info(f"as by user request the download will be done;"
                             f"if it fails please remove edition from gs.json auf year 2017")

            if os.path.exists(f"{user_data[0]['downloadtarget']}/{jahr}/{filenamepattern_local}"):
                logging.info(f"Skip download - already existing "
                             f"'{user_data[0]['downloadtarget']}/{jahr}/{filenamepattern_local}'")
                continue
            try:
                if os.path.exists(f"{user_data[0]['downloadtarget']}/{filenamepattern_download}"):
                    os.remove(f"{user_data[0]['downloadtarget']}/{filenamepattern_download}")
                sleep(5)
                logging.info(f'Try now download of : Jahr {jahr} and Ausgabe {ausgabe} - URL:https://www.gamestar.de/_misc/plus/showbk.cfm?bky={jahr}&bkm={ausgabe}')
                driver.get(f'https://www.gamestar.de/_misc/plus/showbk.cfm?bky={jahr}&bkm={ausgabe}')
                sleep(8)
                try:
                    save_button = wait_de.until(ec.visibility_of_element_located((By.XPATH,
                                                                                  '//*[@id="top_menu_save"]')))
                except TimeoutException:
                    if args.latest:
                        logging.warning('Looks like the page not found is displayed - this edition failed')
                        dl_success = False
                        continue
                    else:
                        logging.warning('Looks like the page not found is displayed - skip this edition')
                        continue
                ActionChains(driver).move_to_element(save_button).click().perform()
                wait_de.until(ec.visibility_of_element_located((By.XPATH, '//p[@class="title"]')))

                wait_de.until(ec.visibility_of_element_located((By.XPATH, "//a[contains(@href, 'complete.pdf')]")))
                driver.find_element_by_xpath("//a[contains(@href, 'complete.pdf')]").click()
                sleep(1)
                result = wait_for_download(f"{user_data[0]['downloadtarget']}/{filenamepattern_download}",
                                           timeout=user_data[0]['downloadtimeout'])
                if result is True:
                    if not os.path.exists(f"{user_data[0]['downloadtarget']}/{jahr}"):
                        os.mkdir(f"{user_data[0]['downloadtarget']}/{jahr}")
                    # Give it time to sync to disk - not clear
                    sleep(2)
                    os.rename(f"{user_data[0]['downloadtarget']}/{filenamepattern_download}",
                              f"{user_data[0]['downloadtarget']}/{jahr}/{filenamepattern_local}")
                else:
                    logging.warning('Download not yet completed - not possible to move by now')
            except TimeoutException as t:
                logging.exception(f'Browser page load failed;maybe edition does not exist;or very slow load '
                                  f'- timeout exception:{t}')
            except Exception as e:
                logging.exception(f'Exception:{e}')
                driver.quit()
    return dl_success

def wait_for_download(filedownloadfullpath, timeout=30):
    logging.debug(f'Download timeout is:[{timeout}]')
    time_out = time() + 2
    while not os.path.exists(f'{filedownloadfullpath}.part') and time() < time_out:
        logging.debug(f'{filedownloadfullpath}.part not yet seen- waiting for first download')

        sleep(2)
    time_out = time() + timeout
    while os.path.exists(f'{filedownloadfullpath}.part') and time() < time_out:
        logging.debug(f'{filedownloadfullpath}.part Seen- waiting')
        sleep(1.5)
    if os.path.exists(f'{filedownloadfullpath}.part'):
        logging.warning('Download still in progress - may need recheck - aborting wait to continue'
                        ' - may complete in background')
        return False
    else:
        logging.info('Download done successful')
        return True


# Loggin set up
LOG_FILE = os.path.dirname(os.path.abspath(__file__)) + '/gsArchivPDFDownloader.log'

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=10)
sh = logging.StreamHandler(sys.stdout)
log_level = logging.getLevelName('INFO')
logger.setLevel(log_level)
if log_level == 10:
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - [%(name)s.%(funcName)s:%(lineno)d] - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
else:
    formatter = logging.Formatter('%(asctime)s:[%(levelname)-5.5s] %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)

json_config_file = 'gs.json'

os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Daten aus dem JSON File laden
with open(json_config_file, 'r') as file:
    user_data = json.loads(file.read())

parser = argparse.ArgumentParser(description='Download a certain year with all editions')
parser.add_argument('-l', '--latest',  action='store_const',
                    const=True, help='try to download always the newest (starting from 2021-03)')
parser.add_argument('-y', '--year', type=int, help='a single year in range [1997-2035]')
args = parser.parse_args()
if args.year and (args.year < 1997 or args.year > 2035):
    parser.error("Select a year within range 1997 to 2035")

logging.info(f"Download location:{user_data[0]['downloadtarget']}")
logging.info(f"filenamepattern_fromserver:{user_data[0]['filenamepattern_fromserver']}")
logging.info(f"filenamepattern_intarget  :{user_data[0]['filenamepattern_intarget']}")

if not os.path.exists(f"{user_data[0]['downloadtarget']}"):
    os.makedirs(f"{user_data[0]['downloadtarget']}")

profile: FirefoxProfile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2)
profile.set_preference('browser.helperApps.alwaysAsk.force', False)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', f"{user_data[0]['downloadtarget']}")

profile.set_preference('plugin.disable_full_page_plugin_for_types', 'application/pdf')
profile.set_preference('pdfjs.disabled', True)
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')

options = Options_FF()
options.headless = False
if args.latest and user_data[0]['browser_display_on_latest'].lower() =="no":
    options.headless = True
driver = webdriver.Firefox(options=options, firefox_profile=profile)

url = 'https://www.gamestar.de/plus/'
wait = WebDriverWait(driver, 20)

# open browser and login
driver.get(url)
logging.info(f"Browser now started with URL:{url} - "
             f"try now to log in with user/password [{user_data[0]['user']}/******]")

wait.until(ec.visibility_of_element_located((By.LINK_TEXT, 'einloggen')))
driver.find_element_by_link_text('einloggen').click()
wait.until(ec.visibility_of_element_located((By.ID, 'loginbox-login-username')))
driver.find_element_by_id('loginbox-login-username').send_keys(user_data[0]['user'])
driver.find_element_by_id('loginbox-login-password').send_keys(user_data[0]['password'])
driver.find_element_by_css_selector('button.btn:nth-child(9)').click()

if args.year:
    year = args.year
    for edition in range(1, 14):
        download_edition(int(year), int(edition), int(year),
                         int(edition), user_data[0]['filenamepattern_fromserver'],
                         user_data[0]['filenamepattern_intarget'])
elif args.latest:
    current_year = datetime.now().year
    # current_year = 2020
    current_month = datetime.now().month
    # current_month = 11
    current_day = datetime.now().day
    max_year_latest = datetime.now().year
    max_month_latest = datetime.now().month

    jahr = user_data[0]['latestdownload'][0]['year']
    ausgabe = user_data[0]['latestdownload'][0]['edition']
    jahr_lastdl = str(jahr)
    ausgabe_lastdl = str(ausgabe)

    if int(ausgabe) == 12:
        logging.debug('Latest downloaded edition was a 12, rollover to next year.')
        jahr = int(jahr) + 1
        ausgabe = 0
        max_month_latest = 1
    else:
        if current_day > 15:
            logging.debug('Later than 15th so try also a next month edition.')
            max_month_latest = max_month_latest + 1

    ausgabe = str(int(ausgabe)+1)

    continue_download = True
    success = True
    while continue_download:
        logging.info(f"Trying now to download the latest version for (Year,Editions) (curMonth/Year)=>"
                     f"({jahr}, {ausgabe}) ({current_month}/{current_year})")
        logging.debug(f"maxMonth, maxYear=>({max_month_latest}, {max_year_latest})")
        filenamepattern_download, filenamepattern_local = filename_modification(
            user_data[0]['filenamepattern_intarget'], user_data[0]['filenamepattern_fromserver'], ausgabe, jahr)
        logging.debug(f'Filepattern(from server)     :[{filenamepattern_download}]')
        logging.debug(f'Filepattern(local for target):[{filenamepattern_local}]')
        if os.path.exists(f"{user_data[0]['downloadtarget']}/{jahr}/{filenamepattern_local}"):
            logging.info(f"Skip download - already existing "
                         f"'{user_data[0]['downloadtarget']}/{jahr}/{filenamepattern_local}'")
            success = True
        else:
            logging.info(f"Process Download for "
                         f"'{user_data[0]['downloadtarget']}/{jahr}/{filenamepattern_local}'")
            success = download_edition(int(jahr), int(ausgabe), int(jahr),
                             int(ausgabe), user_data[0]['filenamepattern_fromserver'],
                             user_data[0]['filenamepattern_intarget'])
        logging.debug(f"success [{success}]")
        if success:
            logging.debug(f"Last success download [{ausgabe_lastdl}/{jahr_lastdl}]")
            jahr_lastdl = str(jahr)
            ausgabe_lastdl = str(ausgabe)

        ausgabe = int(ausgabe)+1
        if int(ausgabe) == 13:
            logging.debug('Roll over in loop to next year')
            ausgabe = 1
            jahr = int(jahr)+1
            if jahr > max_year_latest:
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

else:
    for editions in user_data[0]['editions']:
        for year in editions:
            logging.info(f"(Year,Editions)=>({year}, {editions[year]})")
            for edition in editions[year].split(','):
                download_edition(int(year), int(edition), int(year), int(edition),
                                 user_data[0]['filenamepattern_fromserver'],
                                 user_data[0]['filenamepattern_intarget'])

logging.info(f"Last requested edition downloaded - give job some time (30s) to finish, for no good reason...")
sleep(30)
driver.quit()
logging.info('Job done')
