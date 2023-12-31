import requests
from datetime import datetime
import time

response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params = {"periods" : 60})

def get_price(min, i):

    data = response.json()
    last_data = data["result"][str(min)][i]

    return {"close_time" : last_data[0],
            "open_price" : last_data[1],
            "high_price" : last_data[2],
            "low_price" : last_data[3],
            "close_price" : last_data[4]}


def print_price(data):

    print("時間: " + datetime.fromtimestamp(data["close_time"]).strftime('%Y/%m/%d %H:%M') + "  始値: " + str(data["open_price"]) + "  終値: " + str(data["close_price"]))


def check_candle(data):

    if data["high_price"] - data["low_price"] == 0: return False
    else:
        realbody_rate = abs(data["close_price"] - data["open_price"]) / (data["high_price"] - data["low_price"])
        decrease_rate = data["open_price"] / data["close_price"] - 1

    if data["close_price"] > data["open_price"] or decrease_rate < 0.00005 or realbody_rate < 0.5: return False
    else: return True


def check_acsend(last_data, data):

    if data["close_price"] < last_data["close_price"] and data["open_price"] < last_data["open_price"]:
        return True
    else: 
        return False


last_data = get_price(60, 0)
print_price(last_data)
time.sleep(10)

flag = 0
i = 1


while i < 500:

    data = get_price(60, i)

    if data["close_time"] != last_data["close_time"]:
        print_price(data)

        if flag == 0 and check_candle(data):
            flag = 1
        elif flag == 1 and check_candle(data) and check_acsend(last_data, data):
            print("2本連続で陰線!")
            flag = 2
        elif flag == 2 and check_candle(data) and check_acsend(last_data, data):
            print("3本連続で陰線なので売り!")
            flag = 3
        else:
            flag = 0
        
        last_data["close_time"] = data["close_time"]
        last_data["open_price"] = data["open_price"]
        last_data["close_price"] = data["close_price"]

    i += 1
    time.sleep(0)