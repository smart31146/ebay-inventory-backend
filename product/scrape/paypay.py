import json
from django.conf import settings
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from utils.converttext import convert_text
from utils.outdate import PAYPAY


class ScrapingEngine:
    def scrape_data(self, source_url):
        with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
            settings_attrs = f.read()

        res = json.loads(settings_attrs)

        
        # options.headless = True
        options = webdriver.ChromeOptions() 
        options.add_argument("--headless=new")
        options.add_argument('ignoreHTTPSErrors')

        # try:
        driver = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()), options = options)
        
        driver.set_window_size(2560, 1440)
        
        driver.get(source_url)

        driver.implicitly_wait(5)
        dom = bs(driver.page_source, "html.parser")
        data = {}

        try:
            data['purchase_price'] = dom.find('span', attrs={'class': 'sc-ac2d9669-0 fsBeCG'}).text.replace(',', '')
            # data['purchase_price'] = price.replace('円', '')
            data['product_name'] = dom.find('span', attrs={'class': 'sc-ac2d9669-0 deiJjo'}).text
            data['nothing'] = False


            date = dom.find('span', attrs={'class': 'sc-ac2d9669-0 iA-dHEv'}).text
            
            index = PAYPAY.get(res['paypay'])
            cindex = PAYPAY.get(date)

            if cindex != None and cindex >= index:
                data['nothing'] = True
            pan = dom.find('div', attrs={'class': 'sc-a9056ee8-5 cIZEtZ'}).text
            if pan != "購入手続きへ":
                data['nothing'] = True
                print("sold")
            print("correct", data)
        except:
            print("none exist")
            data['nothing'] = True

        driver.close()
            
        return data
