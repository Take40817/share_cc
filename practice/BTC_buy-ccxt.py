import ccxt
from pprint import pprint

bitflyer = ccxt.bitflyer()
bitflyer.apiKey = ""
bitflyer.secret = ""

order = bitflyer.create_order(
    symbol="BTC/JPY",
    type="limit",
    side="buy",
    price="3500000",
    amount="0.01",
    params={"product_code": "BTC_JPY"},
)

pprint(order["id"])
