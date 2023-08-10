import requests
from datetime import datetime
import time

response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params={"periods": 60})

def get_price(minute, i):
    data = response.json()
    last_data = data["result"][str(minute)][i]

    return {
        "close_time": last_data[0],
        "open_price": last_data[1],
        "high_price": last_data[2],
        "low_price": last_data[3],
        "close_price": last_data[4]
    }

def print_price(data):
    print("時間: " + datetime.fromtimestamp(data["close_time"]).strftime('%Y/%m/%d %H:%M') + "  始値: " + str(data["open_price"]) + "  終値: " + str(data["close_price"]))

def check_bearish_candle(data):
    if data["high_price"] - data["low_price"] == 0: return False
    else:
        realbody_rate = abs(data["close_price"] - data["open_price"]) / (data["high_price"] - data["low_price"])
        increase_rate = data["close_price"] / data["open_price"] - 1

    if data["close_price"] > data["open_price"]:
        return False
    elif increase_rate < 0.00005: return False
    elif realbody_rate < 0.5: return False
    else:
        return True

last_data = get_price(60, 0)
print_price(last_data)
time.sleep(10)

flag = 0
i = 1

while i < 500:
    data = get_price(60, i)

    if data["close_time"] != last_data["close_time"]:
        print_price(data)

        if flag == 0 and check_bearish_candle(data):
            print("陰線を検出しました！")
            flag = 1
        else:
            flag = 0
        
        last_data["close_time"] = data["close_time"]
        last_data["open_price"] = data["open_price"]
        last_data["close_price"] = data["close_price"]

    i += 1
    time.sleep(0)  # 適切な時間間隔を設定してください
