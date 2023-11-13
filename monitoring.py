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
                'Quantity': 0
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
     
    while True:

        # cur_time = datetime.datetime.now().hour
        # print(cur_time,"time", int(cur_time))
        # if int(cur_time)>=22 or int(cur_time) < 1 :
        #     continue
        time.sleep(10)
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


            sql = "SELECT * FROM product_product WHERE deleted = False ORDER BY id ASC"

            cur = conn.cursor()
            cur.execute(sql)

            rows = cur.fetchall()
            title = "商品の価格変動！\n"
            mail_text = ''
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for row in rows:
                    # re_time = datetime.datetime.now().hour
                    # print(re_time,"time", int(re_time))
                    # if int(re_time)>=22 or int(re_time) < 1 :
                    #     break
                    # try:
                    pid = str(row[0])
                    url = row[5]
                    ebay_url = row[6]
                    price = int(row[7])

                    if url == '':
                        continue

                    
                    # if pid != '2041' or pid != '1984':
                    #     continue
                    # # if pan_id > int(pid) :
                    #     continue
                    print(pid, "pan", pan_id)
                    
                    pan_id = int(pid)
                    
                        
                    
                    futures.append(
                        executor.submit(
                            scrape_data, url=url, row=row
                        )
                    )
                    
                    # data = scrape_data(url)
                    
                    # while data == None :
                    #     print("data none")
                    #     data = scrape_data(url)
                    

                    
                pp=0
                
                for future in concurrent.futures.as_completed(futures):
                    re1_time = datetime.datetime.now().hour
                    # print(re_time,"time", int(re_time))
                    # if int(re1_time)>=22 or int(re1_time) < 1 :
                    #     break
                    try:
                        pp+=1
                        data = {}
                        data = future.result()
                        print(pp,": result",data['nothing'])
                        pid = str(data['row'][0])
                        url=data['row'][5]
                        ebay_url = data['row'][6]
                        price = int(data['row'][7])
                        if data['nothing']:
                            sql = "INSERT INTO product_deletedlist (created_at, updated_at, product_name, ec_site, purchase_url, ebay_url, purchase_price, sell_price_en, profit, profit_rate, prima, shipping, quantity, notes, created_by_id, deleted_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            val = (data['row'][1], data['row'][2], data['row'][3], data['row'][4], data['row'][5], data['row'][6], data['row'][7], data['row'][8], data['row'][9], data['row'][10], data['row'][11], data['row'][12], data['row'][13], data['row'][14], data['row'][15], datetime.datetime.now())

                            cur.execute(sql, val)
                            conn.commit()

                            # delete record
                            # sql = "DELETE FROM product_product WHERE id = '" + pid + "'"
                            sql = "UPDATE product_product SET deleted = TRUE WHERE id = '" + pid + "'"

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
                            continue


                        # check variance change
                        if data['purchase_price'] == None :
                            continue
                        purchase_price = int(data['purchase_price'])
                        
                        if price > 0 and abs(purchase_price - price) > int(varience):
                            
                            
                            # add to product_maillist
                            sql = "SELECT * FROM product_maillist WHERE product_id = '" + pid + "'"
                            cur.execute(sql)
                            conn.commit()

                            if cur.fetchone() == None:
                                # print(row[7],'data', data['purchase_price'])
                                if ebay_url != '':
                                    ebay_title=get_ebay_title(ebay_url, ebay_setting)
                                mail_text += '【eBay】' + "\n"
                                if ebay_title != False :
                                    mail_text += 'タイトル：' + ebay_title + "\n"
                                if ebay_title == False :
                                    mail_text += 'タイトル：' + data['row'][3] + "\n"
                                
                                mail_text += 'URL: ' + data['row'][6] + "\n"
                                mail_text += '【フリマ】' + "\n"
                                mail_text += 'タイトル：' + data['product_name'] + "\n"
                                mail_text += 'URL: ' + data['row'][5] + "\n"
                                
                                mail_text += str(price) + '円 → ' + str(purchase_price) + '円' + "\n"
                                # print("mail",mail_text)
                                
                                sql = "INSERT INTO product_maillist(product_id) VALUES('" + pid + "')"
                                cur.execute(sql)
                                conn.commit()
                    
                                # send_mail(FROM, PSW, TO, title, text)

                        else:
                            sql = "SELECT * FROM product_maillist WHERE product_id = '" + pid + "'"
                            cur.execute(sql)
                            conn.commit()

                            # remove from product_maillist
                            if cur.fetchone() != None:
                                sql = "DELETE FROM product_maillist WHERE product_id = '" + pid + "'"
                                cur.execute(sql)
                                conn.commit()
                    except requests.ConnectTimeout:
                        print("ConnectTimeout.")                    
                if mail_text != '' :
                    send_mail(FROM, PSW, TO, title, mail_text)
                    # print("mail", mail_text)
                pan_id = 0
                conn.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print("connection xxx error",error)

        # time.sleep(600)

if __name__ == '__main__':
    main()
