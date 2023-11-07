import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup as bs

from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):

        resp = requests.get(
            url=source_url,
        )
        dom = bs(resp.content, 'html.parser')
        data = {}

        try:
            data['purchase_price'] = int(convert_text(dom.find('dd', attrs={'class': 'Price__value'}).contents[0].strip('円')).replace(',', ''))
            data['product_name'] = convert_text(dom.find('h1', attrs={'class': 'ProductTitle__text'}).text)

            product_date = convert_text(dom.find_all('td', attrs={'class': 'Section__tableData'})[-2].text).replace('（月）', ' ')

            pattern = r'\（\w+\）'

            # Perform the replacement
            product_date = re.sub(pattern, ' ', product_date)

            data['nothing'] = False

            date_format = '%Y.%m.%d %H:%M'
            date1 = datetime.strptime(product_date, date_format)
            date2 = datetime.now()

            if date1 < date2:
                print(date1, date2)
                data['nothing'] = True

        except:
            data['nothing'] = True
            
        return data

