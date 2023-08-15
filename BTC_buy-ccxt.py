import ccxt
from pprint import pprint

bitflyer = ccxt.bitflyer()
bitflyer.apiKey = '2fYygqQpc4ruSmMzmdr7LR'
bitflyer.secret = 'IQ6edS8EInDp5K989rNU9nMiGTVp8dI329T/oomu0iQ='

order = bitflyer.create_order(
       symbol = 'BTC/JPY',
       type = 'limit',
       side = 'buy',
       price = '3500000',
       amount = '0.01',
       params = {"product_code" : "BTC_JPY"})

pprint(order["id"])