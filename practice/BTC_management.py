import ccxt
from pprint import pprint

bitflyer = ccxt.bitflyer()
bitflyer.apiKey = '2fYygqQpc4ruSmMzmdr7LR'
bitflyer.secret = 'IQ6edS8EInDp5K989rNU9nMiGTVp8dI329T/oomu0iQ='

orders = bitflyer.fetch_open_orders(
        symbol = "BTC/JPY",
        params = {"product_code" : "BTC_JPY"})

#pprint(orders)

for item in orders:
    print(item["id"] + " : 注文状況-> " + item["status"])