import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains

import os
import json
from time import sleep, time


def wait_for_download(filedownloadfullpath, timeout=30):
    time_out = time() + 2
    while not os.path.exists(f"{filedownloadfullpath}.part") and time() < time_out:
        logging.debug(f"{filedownloadfullpath}.part not yet seen- waiting for first download")

        sleep(0.5)
    time_out = time() + timeout
    while os.path.exists(f"{filedownloadfullpath}.part") and time() < time_out:
        logging.debug(f"{filedownloadfullpath}.part Seen- waiting")
        sleep(1.5)
    if os.path.exists(f"{filedownloadfullpath}.part"):
        logging.warning("Download still in progress - may need recheck - aborting wait to continue \
              - may complete in background")
        return False
    else:
        logging.info("Download done successful")
        return True


logging.basicConfig(format='%(asctime)s:[%(levelname)-5.5s]  %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
# filename='gsArchivPDFDownloader.log'


# Daten aus dem JSON File laden
with open('gs.json', 'r') as file:
    user_data = json.loads(file.read())

logging.info(f"Download location:{user_data[0]['downloadtarget']}")
if not os.path.exists(f"{user_data[0]['downloadtarget']}"):
    os.makedirs(f"{user_data[0]['downloadtarget']}")

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.helperApps.alwaysAsk.force", False)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", f"{user_data[0]['downloadtarget']}")

profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
profile.set_preference("pdfjs.disabled", True)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
driver = webdriver.Firefox(firefox_profile=profile)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

url = "https://www.gamestar.de/plus/"
wait = WebDriverWait(driver, 20)

# open browser and login
driver.get(url)
logging.info(f"Browser now started with URL:{url} - \
try now to log in with user/password [{user_data[0]['user']}/{user_data[0]['password']}]")

wait.until(ec.visibility_of_element_located((By.LINK_TEXT, "einloggen")))
driver.find_element_by_link_text("einloggen").click()
wait.until(ec.visibility_of_element_located((By.ID, "loginbox-login-username")))
driver.find_element_by_id('loginbox-login-username').send_keys(user_data[0]['user'])
driver.find_element_by_id('loginbox-login-password').send_keys(user_data[0]['password'])
driver.find_element_by_css_selector("button.btn:nth-child(9)").click()

jahr_start = 1998
jahr_end = 2021
ausgaben_max = 13
for jahr in range(jahr_start, jahr_end):
    for ausgabe in range(1, ausgaben_max):
        if os.path.exists(f"{user_data[0]['downloadtarget']}/GameStar_Nr._{ausgabe}_{jahr}.pdf") or \
                os.path.exists(f"{user_data[0]['downloadtarget']}/{jahr}/GameStar_Nr._{ausgabe}_{jahr}.pdf"):
            logging.info(f"Skip download - already existing \
            '{user_data[0]['downloadtarget']}/{jahr}/GameStar_Nr._{ausgabe}_{jahr}.pdf'")
            continue

        try:
            sleep(5)
            logging.info(f"Try now download of : Jahr {jahr} and Ausgabe {ausgabe}")
            driver.get(f'https://www.gamestar.de/_misc/plus/showbk.cfm?bky={jahr}&bkm={ausgabe}')
            sleep(5)
            save_button = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="top_menu_save"]')))
            ActionChains(driver).move_to_element(save_button).click().perform()
            wait.until(ec.visibility_of_element_located((By.XPATH, '//p[@class="title"]')))

            wait = WebDriverWait(driver, 10)
            wait.until(ec.visibility_of_element_located((By.XPATH, "//a[contains(@href, 'complete.pdf')]")))
            driver.find_element_by_xpath("//a[contains(@href, 'complete.pdf')]").click()
            sleep(1)
            result = wait_for_download(f"{user_data[0]['downloadtarget']}/GameStar_Nr._{ausgabe}_{jahr}.pdf",
                                       timeout=30)
            if result is True:
                if not os.path.exists(f"{user_data[0]['downloadtarget']}/{jahr}"):
                    os.mkdir(f"{user_data[0]['downloadtarget']}/{jahr}")
                os.rename(f"{user_data[0]['downloadtarget']}/GameStar_Nr._{ausgabe}_{jahr}.pdf",
                          f"{user_data[0]['downloadtarget']}/{jahr}/GameStar_Nr._{ausgabe}_{jahr}.pdf")
            else:
                logging.warning("Download not yet completed - not possible to move by now")
        except Exception as e:
            logging.exception(f"Exception:{e}")
sleep(30)
driver.quit()
logging.info("Job done")
