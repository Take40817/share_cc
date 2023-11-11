import ccxt
from pprint import pprint

bitflyer = ccxt.bitflyer()
bitflyer.apiKey = ""
bitflyer.secret = ""

orders = bitflyer.fetch_open_orders(
    symbol="BTC/JPY", params={"product_code": "BTC_JPY"}
)

# pprint(orders)

for item in orders:
    print(item["id"] + " : 注文状況-> " + item["status"])
