import environ
import os

from pathlib import Path
import requests
import concurrent.futures
import time
import datetime
import json
from django.conf import settings
from utils.convertcurrency import convert
from product.scrape.engineselector import select_engine
from utils.mail import send_mail
from ebaysdk.trading import Connection
from ebaysdk.shopping import Connection as Shopping
import psycopg2

pan_id = 0

def config():
    env = environ.Env()
    BASE_DIR = Path(__file__).resolve().parent
    env.read_env(str(BASE_DIR / ".env"))

    databases = {
        'host': env('DB_HOST'),
        'db_name': env('DB_NAME'),
        'user': env('DB_USER'),
        'password': env('DB_PASSWORD'),
        'port': env('DB_PORT'),
    }

    return databases

def scrape_data(url,row):
    
    engine = select_engine(url=url)
    if engine:
        engine = engine()
        flag=1
        while flag==1:
            try:
                data = engine.scrape_data(source_url = url)
                data['row']=row
                # print(url, 'scrap success',data)
                return data
            except Exception as err:
                flag=1              
                # print("scrap erro", url)
            # raise err
        
        return data
def get_ebay_title(ebay_url, ebay_setting) :
    if ebay_url == '':
        return False
    
    if ebay_setting['app_id'] == "" or ebay_setting['cert_id'] == "" or ebay_setting['dev_id'] == "" or ebay_setting['ebay_token'] == "":
        return False
    item_number = ebay_url.split("/")[-1]

    try:
        api = Connection(appid = ebay_setting['app_id'], devid = ebay_setting['dev_id'], certid = ebay_setting['cert_id'], token = ebay_setting['ebay_token'], config_file=None)
        item = {
            'Item': {
                'ItemID': item_number.strip(),
            }
        }
        # print("item",item_number)
        try:
            response=api.execute('GetItem', {'ItemID':item_number.strip()})
            # title = response.dumps(dict())
           
            product_title = response.dict()['Item']['Title']
            # print("ebay title",product_title)
            return product_title
        except:
            print("api title get error")
            return False
    
    except:
        print("api title error")
        return False



def revise_item(ebay_url, ebay_setting):
    if ebay_url == '':
        return False
    
    if ebay_setting['app_id'] == "" or ebay_setting['cert_id'] == "" or ebay_setting['dev_id'] == "" or ebay_setting['ebay_token'] == "":
        return False
    
    item_number = ebay_url.split("/")[-1]

    try:
        api = Connection(appid = ebay_setting['app_id'], devid = ebay_setting['dev_id'], certid = ebay_setting['cert_id'], token = ebay_setting['ebay_token'], config_file=None)
        item = {
            'Item': {
                'ItemID': item_number.strip(),
                'Quantity': 1
            }
        }

        try:
            api.execute('ReviseItem', item)
            return True
        except:
            print("api revise error")
            return False
    
    except:
        print("api error")
        return False
    
def getorders(ebay_setting):
    
    if ebay_setting['app_id'] == "" or ebay_setting['cert_id'] == "" or ebay_setting['dev_id'] == "" or ebay_setting['ebay_token'] == "":
        return False
    
    try:
        api = Connection(appid = ebay_setting['app_id'], devid = ebay_setting['dev_id'], certid = ebay_setting['cert_id'], token = ebay_setting['ebay_token'], config_file=None)

        try:
            res = api.execute('GetOrders', {'NumberOfDays': 10})
            orders = json.dumps(res.dict()['OrderArray'])

            return True
        except Exception as err:
            print("api order error,",err)
            return False
    
    except:
        print("api connection err")
        return False

def main():
    global pan_id

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'productmanage.settings')
    params = config()
    global count
    count=0
    while True:
        
        if count == 1 :
            break
        with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
            settings_attrs = f.read()

        setting = json.loads(settings_attrs)

        f.close()

        ebay_setting = {
            'app_id' : '',
            'cert_id' : '',
            'dev_id' : '',
            'ebay_token' : ''
        }

        FROM = setting['email_address']
        PSW = setting['psw']
        varience = setting['variable_price']
        print("from",FROM,"pw",PSW)
        try:
            conn = psycopg2.connect(
                database = params['db_name'],
                host = params['host'],
                user = params['user'],
                password = params['password'],
                port = params['port']
            )
            count = count +1
            sql = "SELECT email, app_id, cert_id, dev_id, ebay_token FROM users_user WHERE is_superuser = TRUE"

            cur = conn.cursor()
            cur.execute(sql)
            row = cur.fetchone()

            if row == None:
                continue

            TO = row[0]

            ebay_setting = {
                'app_id' : row[1],
                'cert_id' : row[2],
                'dev_id' : row[3],
                'ebay_token' : row[4]
            }


            sql = "SELECT * FROM product_deletedlist ORDER BY id DESC"

            cur = conn.cursor()
            cur.execute(sql)

            rows = cur.fetchall()
            title = "商品の再登録！\n"
            mail_text = ''
            
            for row in rows:
                current_date = datetime.datetime.now()
                given_date = datetime.datetime.strptime(row[15], "%Y-%m-%d %H:%M:%S.%f")
                days_ago = (current_date - given_date).days
                # try:
                pid = str(row[0])
                url = row[5]
                ebay_url = row[6]
                if days_ago>30:
                    continue

                if url == '':
                    continue

                
                # if pid != '66':
                #     continue
                # # if pan_id > int(pid) :
                #     continue
                print(pid, "pan: ", row, "ago: ", days_ago)
                
                pan_id = int(pid)
                
                data = scrape_data(url, row)
                
                # while data == None :
                #     print("data none")
                #     data = scrape_data(url)
                try:
                  
                   
                    pid = str(data['row'][0])
                    url=data['row'][5]
                    ebay_url = data['row'][6]
                    print("test nothing",data['nothing'] )
                    if data['nothing'] !=True:
                        sql = "DELETE FROM product_deletedlist WHERE id = '" + pid + "'"
                        
                        cur.execute(sql)
                        conn.commit()
                        
                        
                        # delete record
                        # sql = "DELETE FROM product_product WHERE id = '" + pid + "'"
                        sql = "UPDATE product_product SET deleted = FALSE WHERE ebay_url = '" + data['row'][6] + "'"


                        cur.execute(sql)
                        conn.commit()
                        # del_title= "delete alarm"
                        # del_message= ''
                        # if ebay_url != '':
                        #     del_ebay_title=get_ebay_title(ebay_url, ebay_setting)
                        # del_message += '【eBay】' + "\n"
                        # if del_ebay_title != False :
                        #     del_message += 'タイトル：' + del_ebay_title + "\n"
                        # if del_ebay_title == False :
                        #     del_message += 'タイトル：' + row[3] + "\n"
                        
                        # del_message += 'URL: ' + ebay_url + "\n"
                        # del_message += '【フリマ】' +data['row'][5]+ "\n"
                        
                        # send_mail(FROM, PSW, TO, del_title, del_message)
                        # set ebay product quantity 0
                        if ebay_url != '':
                            revise_item(ebay_url, ebay_setting)
                        print(url, "success recover",ebay_url )


                    
                except requests.ConnectTimeout:
                    print("ConnectTimeout.")                    
            
            pan_id = 0
            conn.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print("connection xxx error",error)

        # time.sleep(600)

if __name__ == '__main__':
    main()
