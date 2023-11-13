import time
import json
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from django.conf import settings

from utils.outdate import MERCARI

class ScrapingEngine:
    def scrape_data(self, source_url):
        data = {}
        data['nothing'] = False
        with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
            settings_attrs = f.read()

        
        res = json.loads(settings_attrs)
        
        options = webdriver.ChromeOptions() 
        options.headless = True

        # try:
        driver = webdriver.Chrome(options = options, service = ChromeService(ChromeDriverManager().install()))
        # except:
        #     print('driver error')
        #     data['faild'] = True
        #     return data

        driver.get(source_url)

        driver.implicitly_wait(5)
        loaded = None
        while loaded is None:
            # print("none")
            dom = bs(driver.page_source, "html.parser")
            loaded = dom.find('div', attrs={'data-testid': 'price'}) or dom.find('div', attrs={'data-testid': 'product-price'}) or dom.find('div', attrs={'class': 'merEmptyState'})
            # if loaded == None:
            #     driver.close()
            #     driver = webdriver.Chrome(options = options, service = ChromeService(ChromeDriverManager().install()))
            #     driver.get(source_url)
            # print('2',loaded)   
            # time.sleep(1)
        if (dom.find('div', attrs={'class', 'merEmptyState'})) :
            print("delete empty", source_url)
            try :
                if (dom.find('div', attrs={'data-testid': 'price'})) == None :
                    content=driver.find_element(By.XPATH, "//*[@id='main']/div/div[1]/p").text
                    if content == 'この商品は削除されました' or content != None :
                        print("delete source", source_url)
                        data['nothing'] = True
                        driver.close()
                        return data
            except :

                print('del continue',source_url)
            
        price_dom = dom.find('div', attrs={'data-testid': 'price'}) or dom.find('div', attrs={'data-testid': 'product-price'})
        data['purchase_price'] = int(price_dom.find_all('span')[-1].text.replace(',', ''))
        # data['purchase_price'] = int(driver.find_element(By.XPATH, "//*[@id='item-info']/section[1]/section[1]/div/div/span[2]").text.replace(',', '')) 
        data['product_name'] = driver.find_element(By.XPATH, "//*[@id='item-info']/section[1]/div[1]/div/div/h1").text
        # title_dom = dom.find('div', attrs={'data-testid': 'name'}) or dom.find('div', attrs={'data-testid': 'display-name'})
        # data['product_name'] = convert_text(title_dom.div.h1.text)
        
        product_date = driver.find_element(By.XPATH, "//*[@id='item-info']/section[2]/p").text

        data['nothing'] = False

        index = MERCARI.get(res['mercari'])
        cindex = MERCARI.get(product_date)
        
        if cindex != None and index <= cindex:
            print(source_url,"delete index",cindex)
            data['nothing'] = True

        button = driver.find_elements(By.CLASS_NAME, "merButton")[-1].find_elements(By.TAG_NAME, "button")[0].text

        if button == '売り切れました':
            print('delete sold', source_url)
            data['nothing'] = True

        driver.close()
        # print("scrap result", data)
        return data
