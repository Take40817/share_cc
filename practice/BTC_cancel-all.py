import ccxt
from pprint import pprint

bitflyer = ccxt.bitflyer()
bitflyer.apiKey = ''
bitflyer.secret = ''

orders = bitflyer.fetch_open_orders(
        symbol = "BTC/JPY",
        params = {"product_code" : "BTC_JPY"})

print("注文取消し前")

for item in orders:
    print(item["id"] + " : 注文状況-> " + item["status"])
    bitflyer.cancel_order(
            symbol = "BTC/JPY",
            id = item["id"],
            params = {"product_code" : "BTC_JPY"})
    
orders_aft = bitflyer.fetch_open_orders(
        symbol = "BTC/JPY",
        params = {"product_code" : "BTC_JPY"})
    
print()
print("注文取消し後")

if orders_aft == []:
    print("注文はすべて消されました")
else:
    for item in orders_aft:
        print(item["id"] + " : 注文状況-> " + item["status"])