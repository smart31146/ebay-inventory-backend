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
        options.add_argument("--headless=new")
        options.add_argument('ignoreHTTPSErrors')

        # try:
        driver = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()), options = options)
        driver.set_window_size(2560, 1440)
        # except:
        #     print('driver error')
        #     data['faild'] = True
        #     return data

        driver.get(source_url)

        driver.implicitly_wait(5)
        # loaded = None
        # pan=0
        # while loaded is None:
            
            
        #     dom = bs(driver.page_source, "html.parser")
        #     loaded = dom.find('div', attrs={'data-testid': 'price'}) or dom.find('div', attrs={'data-testid': 'product-price'}) or dom.find('div', attrs={'class': 'merEmptyState'})
        #     if loaded == None and pan>10:
        #         driver.close()
        #         driver = webdriver.Chrome(options = options, service = ChromeService(ChromeDriverManager().install()))
        #         driver.set_window_size(2560, 1440)
        #         driver.get(source_url)
        #         pan=0
        #         print("none", source_url)
        #         driver.implicitly_wait(5)
        #         dom = bs(driver.page_source, "html.parser")
        #         time.sleep(3)
        #         loaded = dom.find('div', attrs={'data-testid': 'price'}) or dom.find('div', attrs={'data-testid': 'product-price'}) or dom.find('div', attrs={'class': 'merEmptyState'})

                # print('2',loaded)   
            # time.sleep(1)
            # if pan < 10 and loaded==None :
            #     pan=pan+1
        try :
            pan_empty = driver.find_elements(By.CLASS_NAME,"merEmptyState")[0].find_element(By.TAG_NAME,"p").text
            if pan_empty!= None :
                print("delete source empty", source_url)
                data['nothing'] = True
                driver.close()
                return data        
        except:
            print("no empty")    
        # if (dom.find('div', attrs={'class', 'merEmptyState'})) :
        #     print("delete empty", source_url)
        #     try :
        #         if (dom.find('div', attrs={'data-testid': 'price'})) == None :
        #             content=driver.find_element(By.XPATH, "//*[@id='main']/div/div[1]/p").text
        #             print("del content",content)
        #             if content == 'この商品は削除されました' or content != None :
        #                 print("delete source", source_url)
        #                 data['nothing'] = True
        #                 driver.close()
        #                 return data
        #     except :

        #         print('del continue',source_url)
        print("test", source_url)           
        # pan=driver.find_element(By.XPATH, "//*[@id='main']/article/div[1]/section/div/div/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div").get_attribute("aria-label")
        pan_items = driver.find_elements(By.CLASS_NAME, "merItemThumbnail")
        for item in pan_items :
            
            if item.get_attribute("aria-label") == '売り切れ':
                print('delete sold', source_url)
                data['nothing'] = True
                return data
            # print(source_url,"okay",item.get_attribute("aria-label"))
        
                   
        # price_dom = dom.find('div', attrs={'data-testid': 'price'}) or dom.find('div', attrs={'data-testid': 'product-price'})
        # price = int(driver.find_element(By.CSS_SELECTOR,"div[data-testid='price']").find_elements(By.TAG_NAME,"span")[1].text.replace(',', ''))
        # price=int(driver.find_element(By.ID,"item-info").find_elements(By.TAG_NAME,"span")[-1].text.replace(',', ''))
        # print("test price", price)
        # data['purchase_price'] = int(price_dom.find_all('span')[-1].text.replace(',', ''))
        data['purchase_price'] = int(driver.find_element(By.CSS_SELECTOR,"div[data-testid='price']").find_elements(By.TAG_NAME,"span")[1].text.replace(',', ''))
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

        

        driver.close()
        # print("scrap result", data)
        return data
