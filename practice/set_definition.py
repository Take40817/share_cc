import requests
from datetime import datetime
import time


def get_price(min):
    
    response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params = {"periods" : min})
    response = response.json()

    data = response["result"][str(min)][-2]

    close_time = data[0]
    open_price = data[1]
    close_price = data[4]

    return close_time, open_price, close_price


def print_price(close_time, open_price, close_price):

    print("時間: " + datetime.fromtimestamp(close_time).strftime('%Y/%m/%d %H:%M') + "  始値: " + str(open_price) + "  終値: " + str(close_price))


last_time = 0
while True:

    close_time, open_price, close_price = get_price(60)
    
    if close_time != last_time:

        last_time = close_time
        print_price(close_time, open_price, close_price)

    time.sleep(10)