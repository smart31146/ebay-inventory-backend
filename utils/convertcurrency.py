import requests
# url = 'https://api.exchangerate-api.com/v4/latest/USD'
# currencies = requests.get(url).json()['rates']

def convert(from_currency, to_currency, amount): 
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    currencies = requests.get(url).json()['rates']
    if from_currency != 'USD' : 
        amount = amount / currencies[from_currency] 
    amount = round(amount * currencies[to_currency], 4) 

    return amount

def getCurrentRate(currency):
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    currencies = requests.get(url).json()['rates']
    print("testrate api", currencies[currency])
    return currencies[currency]