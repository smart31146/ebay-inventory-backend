import json

def sell_set_formula(profitRate:float, purchase_price:int, prima:float, shipping:float, setting_attr:json):

    purchase_price = purchase_price + prima

    fvf = float(setting_attr['fvf'])
    oversea = float(setting_attr['oversea'])
    payoneer = float(setting_attr['payoneer'])
    fedex = float(setting_attr['fedex'])
    rate = float(setting_attr['rate'])

    if fvf != 0:
        fvf = fvf / 100

    if oversea != 0:
        oversea = oversea / 100

    if payoneer != 0:
        payoneer = payoneer / 100

    if fedex != 0:
        fedex = fedex / 100
   
    ebay_sell_price = (purchase_price + shipping * (1+fedex)) / (((1-fvf-oversea) *(1-payoneer)- profitRate/100)*rate)
    integer_part = int(ebay_sell_price)
    # Combine integer part with .99
    result = integer_part + 0.99
    
    return result
