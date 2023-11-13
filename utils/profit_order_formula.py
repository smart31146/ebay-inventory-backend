import json

def profit_order_formula(sell_price:float, purchase_price:int, prima:float, shipping:float, setting_attr:json):

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
    profit = rate * sell_price * 0.98 - purchase_price -shipping
    # profit = (sell_price - sell_price * fvf - sell_price * oversea) * (rate - rate * payoneer) - purchase_price - shipping - shipping * fedex

    return profit
