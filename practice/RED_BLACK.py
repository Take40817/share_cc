import requests
from datetime import datetime
import time


def get_price(min):

    response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params = {"periods" : min})
    data = response.json()
    last_data = data["result"][str(min)][-2]

    return {"close_time" : last_data[0],
            "open_price" : last_data[1],
            "high_price" : last_data[2],
            "low_price" : last_data[3],
            "close_price" : last_data[4]}


def print_price(data):

    print("時間: " + datetime.fromtimestamp(data["close_time"]).strftime('%Y/%m/%d %H:%M') + "  始値: " + str(data["open_price"]) + "  終値: " + str(data["close_price"]))


def check_candle(data):

    realbody_rate = abs(data["close_price"] - data["open_price"]) / (data["high_price"] - data["low_price"])
    increase_rate = data["close_price"] / data["open_price"] - 1

    if data["close_price"] < data["open_price"]: return False
    elif increase_rate < 0.00005: return False
    elif realbody_rate < 0.5: False
    else: return True


def check_candle_black(data):

    realbody_rate = abs(data["close_price"] - data["open_price"]) / (data["high_price"] - data["low_price"])
    increase_rate = data["close_price"] / data["open_price"] - 1

    if data["close_price"] > data["open_price"]: return False
    elif increase_rate < 0.00005: return False
    elif realbody_rate < 0.5: False
    else: return True


def check_acsend(last_data, data):

    if data["close_price"] > last_data["close_price"] and data["open_price"] > last_data["open_price"]:
        return True
    else: 
        return False
    

def check_acsend_black(last_data, data):

    if data["close_price"] < last_data["close_price"] and data["open_price"] < last_data["open_price"]:
        return True
    else: 
        return False


last_data = get_price(60)
print_price(last_data)
flag = 0


while True:

    data = get_price(60)

    if data["close_time"] != last_data["close_time"]:
        print_price(data)

        if flag == (0 or -1 or -2 or -3) and check_candle(data):
            flag = 1
        elif flag == 1 and check_candle(data) and check_acsend(last_data, data):
            print("2本連続で陽線!")
            flag = 2
        elif flag == 2 and check_candle(data) and check_acsend(last_data, data):
            print("3本連続で陽線なので買い!")
            flag = 3
        
        elif flag == (0 or 1 or 2 or 3) and check_candle_black(data):
            flag = -1
        elif flag == -1 and check_candle_black(data) and check_acsend_black(last_data, data):
            print("2本連続で陰線!")
            flag = -2
        elif flag == -2 and check_candle_black(data) and check_acsend_black(last_data, data):
            print("3本連続で陰線なので売り!")
            flag = -3
        
        else:
            flag = 0
        
        last_data["close_time"] = data["close_time"]
        last_data["open_price"] = data["open_price"]
        last_data["close_price"] = data["close_price"]

    time.sleep(10)