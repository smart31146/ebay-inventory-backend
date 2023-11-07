def scrape_data(self, source_url):
        options = webdriver.ChromeOptions() 
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(source_url)
        loaded = None
        data = {}
        data['quantity'] = 1
        while loaded is None:
            dom = bs(driver.page_source, "html.parser")
            loaded = dom.find('div', attrs={'data-testid': 'price'}) or dom.find('div', attrs={'data-testid': 'product-price'}) or dom.find('div', attrs={'class': 'merEmptyState'})
            time.sleep(2)

        if(dom.find('div', attrs={'class', 'merEmptyState'})):
            data['quantity'] = 0
            return data
        title_dom = dom.find('div', attrs={'data-testid': 'name'}) or dom.find('div', attrs={'data-testid': 'display-name'})
        data['title_jp'] = convert_text(title_dom.div.h1.text)
        price_dom = dom.find('div', attrs={'data-testid': 'price'}) or dom.find('div', attrs={'data-testid': 'product-price'})
        data['price_jp'] = int(price_dom.find_all('span')[-1].text.replace(',', ''))
        data['description_jp'] = [convert_text(dom.find('pre', attrs={'data-testid': 'description'}).text)]
        data['photos'] = []
        photos_wrapper = dom.find('div', attrs={'class', 'slick-track'}).contents
        for photo_wrapper in photos_wrapper:
            data['photos'].append(
                {
                    'path': photo_wrapper.find('img')['src']
                }
            )

        return data