import requests
from datetime import datetime
import time


response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?periods=60")
response = response.json()

last_data = response["result"]["60"][-2]
last_time = datetime.fromtimestamp(last_data[0]).strftime('%Y/%m/%d %H:%M')
time.sleep(10)

while True:
    
    
    response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?periods=60")
    response = response.json()

    data = response["result"]["60"][-2]

    close_time = datetime.fromtimestamp(data[0]).strftime('%Y/%m/%d %H:%M')
    open_price = data[1]
    close_price = data[4]
    
    if last_time != close_time:
        print("時間: " + close_time + "  始値: " + str(open_price) + "  終値: " + str(close_price))
        last_time = close_time
    
    time.sleep(10)