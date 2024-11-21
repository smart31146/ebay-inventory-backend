import time
import json
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from django.conf import settings
import requests
import re

from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        
        resp = requests.get(
            url=source_url,
        )
        data = {}
        
        print("test hardoff", source_url)
        try:
            item_detail = bs(resp.content, "html.parser").find('div', attrs={'class': 'product-detail'})
            data = {}
            data['product_name'] = item_detail.find('div', attrs={'class': 'product-detail-name'}).h1.text
            data['purchase_price'] = int(item_detail.find('span', attrs={'class': 'product-detail-price__main'}).text.replace(',', ''))
            pan = convert_text(item_detail.find('button', attrs={'class': 'cart-add-button'}).span.text)
            
            if pan=="カートに入れる": 
              
                data['nothing'] = False
            else :
                data['nothing'] = True
               
            # data['description_jp'] = []
            # table= item_detail.find('div', attrs={'id': 'panel1'}).table.contents
            # for row in table:
            #     if hasattr(row, 'contents'):
            #         if(len(row.contents) == 2):
            #             description = convert_text(row.contents[0].text + ': ' + row.contents[1].text)
            #         elif(len(row.contents) == 5):
            #             description = convert_text(row.contents[1].text + ': ' + row.contents[3].text)
                    
            #         data['description_jp'].append(description)

            # data['photos'] = []
            # photos = item_detail.find('div', attrs={'class': 'product-detail-images-main'}).find_all('img')
            # for photo in photos:
            #     data['photos'].append(
            #         {
            #             'url': photo['src']
            #         }
            #     )
        except: 
            data['nothing'] = True
       
        return data
