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

        options = webdriver.ChromeOptions() 
        options.headless = True
        driver = webdriver.Chrome(options = options, service = ChromeService(ChromeDriverManager().install()))
        
        driver.get(source_url)

        driver.implicitly_wait(5)
        dom = bs(driver.page_source, "html.parser")
        data = {}

        try:
            price = dom.find('span', attrs={'class': 'sc-16898e71-0 jQeuFi ItemPrice__Component'}).text.replace(',', '')
            data['purchase_price'] = price.replace('円', '')
            data['product_name'] = dom.find('span', attrs={'class': 'sc-b9519356-0 lkCzRl'}).text
            data['nothing'] = False

            date = dom.find('span', attrs={'class': 'sc-b9519356-0 kFtkcq'}).text
            
            index = PAYPAY.get(res['paypay'])
            cindex = PAYPAY.get(date)

            if cindex != None and cindex >= index:
                data['nothing'] = True

        except:
            data['nothing'] = True

        driver.close()
            
        return data
