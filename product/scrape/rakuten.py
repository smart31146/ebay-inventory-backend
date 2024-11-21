import time
import json
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from django.conf import settings
import requests
import re

from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        
        resp = requests.get(
            url=source_url,
        )
        loaded = None
        data = {}
        count = 0
        options = webdriver.ChromeOptions() 
        options.add_argument("--headless=new")
        options.add_argument('ignoreHTTPSErrors')

        # try:
        driver = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()), options = options)
        driver.set_window_size(2560, 1440)
        driver.get(source_url)

        # driver.implicitly_wait(5)
        wait = WebDriverWait(driver, 5)
        print("test rakuten", source_url)
        button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='かごに追加']")))

    # Check if the button has the 'disabled' attribute
        is_disabled_attr = button.get_attribute('disabled') is not None
        # while loaded is None:
        #     dom = bs(resp.content, "html.parser")
        #     loaded = dom.find('div', attrs={'id': 'priceCalculationConfig'})['data-price']
        #     time.sleep(5)
        #     count+=1
        #     if count == 5:
        #         data['nothing'] = True
        #         return data
        try:
            if is_disabled_attr == True:
                data['nothing'] = True
                driver.close()
                return data
            dom = bs(resp.content, "html.parser")
            data['product_name'] = convert_text(dom.find('span', attrs={'class': 'normal_reserve_item_name'}).b.text)
         
            data['purchase_price'] = int(dom.find('div', attrs={'id': 'priceCalculationConfig'})['data-price'])
            print("test rakuten rerulst2", data)
            data['nothing'] = False
            # sold = dom.find('div', attrs={'class': 'text-display--1Iony type-body--1W5uC size-medium--JpmnL align-left--1hi1x color-crimson--_Y7TS  layout-inline--1ajCj'})
            # print("test sold", dom)
            print(f"Is button disabled: {is_disabled_attr}")
            # pan = convert_text(dom.find('div', attrs={'class': 'floating-cart-wrapper'}).button.span.text)
            # print("test rakuten pan", pan)
        # if dom.find('ul', attrs={'class': 'point-summary__campaign___2KiT- point-summary__multiplier-up___3664l point-up'}):
        #     point_info = dom.find('ul', attrs={'class': 'point-summary__campaign___2KiT- point-summary__multiplier-up___3664l point-up'}).find_all('li')
        #     multi = int(point_info[-1].text.strip('倍UP'))
        #     data['point'] = int(data['price_jp']*multi/100)
        # data['description_jp'] = []
        # descriptions = dom.find('span', attrs={'class': 'item_desc'})
        # if descriptions:
        #     for description in descriptions:
        #         description = convert_text(description.text)
        #         if(description):
        #             data['description_jp'].append(description)
        # data['photos'] = []
        # photos = dom.find_all('meta', attrs={'itemprop': 'image'})
        # for photo in photos:
        #     data['photos'].append(
        #         {
        #             'url': photo['content']
        #         }
        #     )
        except:
            print("test rakuten except", source_url)
            driver.close()
            data['nothing'] = True
        print("rakuten result", data)
        driver.close()
        return data