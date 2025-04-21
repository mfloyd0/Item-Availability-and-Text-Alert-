import time
import logging
import confi

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Messenger
from mysql.connector import connect, Error
from datetime import date
from urllib.parse import urlparse


host = confi.host
dbUser = confi.dbUser
dbPassword = confi.dbPassword
database = confi.dataBase

today = str(date.today())

def log_details():
    logging.basicConfig(
        filename=f"AutomationLog-{today}.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %p"
    )
    return logging.getLogger()

def sql():
    logger = log_details()
    result = tuple()
    try:
        with connect(
                host=host,
                user=dbUser,
                password=dbPassword,
                database=database,
        ) as db:
            mycursor = db.cursor()
            mycursor.execute("SELECT * FROM links")
            result = mycursor.fetchall()
    except Error as e:
        logger.info(e)
        print(e)
    return result


def remove(id):
    logger = log_details()
    delstatmt = "delete from dbo.links where ID = %s"
    try:
        with connect(
                host=host,
                user=dbUser,
                password=dbPassword,
                database=database,
        ) as db:
            mycursor = db.cursor()
            mycursor.execute(delstatmt, (id,))
            db.commit()
    except Error as e:
        logger.info(e)
        print(e)


def updateFlag(id, flag):
    logger = log_details()
    statment = "UPDATE `dbo`.`link` SET `Flag` = %s WHERE (`ID` = %s);"
    try:
        with connect(
                host=host,
                user=dbUser,
                password=dbPassword,
                database=database,
        ) as db:
            mycursor = db.cursor()
            mycursor.execute(statment, (flag, id,))
            db.commit()
    except Error as e:
        logger.info(e)
        print(e)


def bestBuy(link, cell, site):
    logger = log_details()
    status = False
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.get(link)
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'fulfillment-add-to-cart-button'))
        )
        titleSection = driver.find_element(By.CLASS_NAME, "shop-product-title")
        itemTitle = titleSection.find_element(By.CLASS_NAME, "sku-title")

        #message = "Item Available at Bestbuy \n \n {} \n \n {}".format(itemTitle.text, link).encode('utf-8')
        message = "Item Available at {} \n \n {}".format(site ,itemTitle.text).encode('utf-8')

        elements2 = driver.find_elements(By.CLASS_NAME, 'fulfillment-add-to-cart-button')
        for e in elements2:
            if "Add to Cart" in e.text:
                Messenger.text(message, cell)
                status = True
                break
            if "Sold Out" in e.text:
                logger.info(f"{itemTitle.text} Sold Out")
                break

    except NoSuchElementException:
        print("element not found")
        logger.info("Element not found")
    except TimeoutException:
        print("timeout error")
        logger.info("Timeout Error")
    except:
        print("error")
        logger.info("Unexpected Error")
    finally:
        driver.close()
        driver.quit()
        return status

def target(link, cell, site):
    status = False
    logger = log_details()
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.get(link)
    #driver.implicitly_wait(5)
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test=fulfillment-cell-shipping]"))
        )
        shipping = driver.find_element(By.CSS_SELECTOR, "button[data-test=fulfillment-cell-shipping]").find_element(
            By.CLASS_NAME, "fulfillment-message")

        itemTitle = driver.find_element(By.CSS_SELECTOR, "h1[data-test=product-title]")


        message = "Item Available at {} \n \n {}".format(site,itemTitle.text).encode('utf-8')

        if "Arrives by" in shipping.text:
            Messenger.text(message, cell)
            status = True
        if "Not available" in shipping.text:
            logger.info(f"{itemTitle.text} Sold Out")


    except NoSuchElementException:
        print("element not found")
        logger.info("Element not found")
    except TimeoutException:
        print("timeout error")
        logger.info("Timeout Error")
    except:
        print("error")
        logger.info("Unexpected Error")
    finally:
        driver.close()
        driver.quit()
        return status

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    result = sql()

    for row in result:
        rowNum = row[0]
        flag = row[3]
        link = row[2]
        number = row[1]
        hostUrl = urlparse(link).hostname
        targetSite = hostUrl.split('.')[1]
        if targetSite == 'bestbuy':
            stat = bestBuy(link,number, targetSite)
        elif targetSite == 'target':
            stat = target(link,number,targetSite)
        time.sleep(3)
        if stat:
            flag += 1
            if flag > 3:
                remove(rowNum)
            else:
                updateFlag(rowNum, flag)

print("done")
