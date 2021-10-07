from itertools import zip_longest
import csv
import json
import re
import time
import traceback
import requests
from bs4 import BeautifulSoup
from time import sleep
from openpyxl import load_workbook
import cloudscraper
import threading
from datetime import date
import json
import xlsxwriter
from lxml import etree
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

filter_tds = []
with open('fmsca09-03-21.csv', 'w+', newline='', encoding='UTF-8') as csvfile:
    wr = csv.writer(csvfile)
    wr.writerow(
        ['url1', 'url2', 'MC NUMBER', 'legal_name', 'ISAUTH', 'US_DOT',
         'url3', 'telephone', 'email'])
    print('done')


def implicit_wait_break(driver, delay, xpath):
    while True:
        try:
            myElem = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return True
            break
        except TimeoutException:
            return False
            break
            pass


def implicit_wait(driver, delay, xpath):
    while True:
        try:
            myElem = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            break
        except TimeoutException:
            pass


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


driver = webdriver.Chrome(ChromeDriverManager().install())
for x in range(0, 9):
    driver.get('https://li-public.fmcsa.dot.gov/LIVIEW/pkg_menu.prc_menu')
    implicit_wait(driver, 3, '//*[@id="menu"]')
    driver.find_element_by_xpath('//*[@id="menu"]').click()
    sleep(2)
    driver.find_element_by_xpath('//option[@value = "FED_REG"]').click()
    sleep(1)
    driver.find_element_by_xpath('//input[@alt="Menu Go"]').click()
    implicit_wait(driver, 3, '//input[@value = "HTML Detail"]')
    driver.find_elements_by_xpath('//input[@value = "HTML Detail"]')[x].click()
    implicit_wait(driver, 3, '//u[text()="FITNESS-ONLY"]/../p/table/tbody/tr/td[2]')
    tds = driver.find_elements_by_xpath(
        '//td[contains(text(),"Interstate common carrier")]/../preceding-sibling::tr[1]/td[2]')
    company_names = []
    for td in tds:
        name = td.text.replace(td.find_element_by_xpath('div').text, '')
        print(name)
        company_names.append(name)
    print(company_names)
    print(len(company_names))
    for company_name in company_names:
        driver.get('https://safer.fmcsa.dot.gov/CompanySnapshot.aspx')
        implicit_wait(driver, 3, '//*[@id="3"]')
        driver.find_element_by_xpath('//*[@id="3"]').click()
        driver.find_element_by_xpath('//*[@id="4"]').send_keys(company_name.strip('\n'))
        driver.find_element_by_xpath('//input[@value="Search"]').click()
        flag = implicit_wait_break(driver, 10, '//th/b/a')
        if flag:
            url2 = driver.current_url
            driver.find_element_by_xpath('//th/b/a').click()
            implicit_wait_break(driver, 5, '//table')
            if 'NOT AUTHORIZED' in driver.find_element_by_xpath('//a[contains(text(),"Operating Status")]/../../td').text:
                driver.find_element_by_xpath('//a[contains(text(),"SMS Results")]').click()
                implicit_wait(driver,3,'//*[@id="fmcsa-header"]')
                url3 = driver.current_url
                try:
                    driver.find_element_by_xpath('//a[contains(text(),"Carrier Registration Details")]').click()
                except:
                    continue
                    pass

                implicit_wait(driver, 3, '//label[contains(text(),"Legal Name")]/../span')
                legal_name = driver.find_element_by_xpath('//label[contains(text(),"Legal Name")]/../span').text
                US_DOT = driver.find_element_by_xpath('//label[contains(text(),"U.S. DOT")]/../span').text
                try:
                    address = driver.find_element_by_xpath('//label[contains(text(),"Address")]/../span').text
                except:
                    address = ''
                    pass
                try:
                    telephone = driver.find_element_by_xpath('//label[contains(text(),"Telephone")]/../span').text
                except:
                    telephone = ''
                    pass
                try:
                    email = driver.find_element_by_xpath('//label[contains(text(),"Email")]/../span').text
                except:
                    email = ''
                    pass
                with open('fmsca09-03-21.csv', 'a+', newline='', encoding='UTF-8') as csvfile:
                    wr = csv.writer(csvfile)
                    wr.writerow(
                        ['https://safer.fmcsa.dot.gov/CompanySnapshot.aspx', url2, 'MC NUMBER', legal_name, 'UNAUTHORIZED', US_DOT, url3, telephone, email])
                    print('done')
            else:
                continue
