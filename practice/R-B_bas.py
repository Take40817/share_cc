import requests
from datetime import datetime
import time

response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params = {"periods" : 60})


def get_price(min, i):

    data = response.json()
    return {"close_time" : data["result"][str(min)][i][0],
            "open_price" : data["result"][str(min)][i][1],
            "high_price" : data["result"][str(min)][i][2],
            "low_price" : data["result"][str(min)][i][3],
            "close_price" : data["result"][str(min)][i][4]}


def print_price(data):

    print("時間: " + datetime.fromtimestamp(data["close_time"]).strftime('%Y/%m/%d %H:%M') + "  始値: " + str(data["open_price"]) + "  終値: " + str(data["close_price"]))


# 各ローソク足がエントリーの条件（陽線）を満たしているか確認する関数
def check_candle(data):

    if data["high_price"] - data["low_price"] == 0: return False
    else:
        realbody_rate = abs(data["close_price"] - data["open_price"]) / (data["high_price"] - data["low_price"])
        increase_rate = data["close_price"] / data["open_price"] - 1        

    if data["close_price"] < data["open_price"]: return False
    elif increase_rate < 0.00005: return False
    elif realbody_rate < 0.5: return False
    else: return True


def check_candle_black(data):

    if data["high_price"] - data["low_price"] == 0: return False
    else:
        realbody_rate = abs(data["close_price"] - data["open_price"]) / (data["high_price"] - data["low_price"])
        decrease_rate = data["open_price"] / data["close_price"] - 1

    if data["close_price"] > data["open_price"]: return False
    elif decrease_rate < 0.00005: return False
    elif realbody_rate < 0.5: return False
    else: return True


# ローソク足の始値・終値が連続で切りあがってるか確認する関数
def check_ascend(data, last_data):

    if data["close_price"] > last_data["close_price"] and data["open_price"] > last_data["open_price"]:
        return True
    else:
        return False
    

def check_acsend_black(data, last_data):

    if data["close_price"] < last_data["close_price"] and data["open_price"] < last_data["open_price"]:
        return True
    else: 
        return False
    

# 買いシグナルが点灯したら指値で買い注文する関数
def bs_signal(data, last_data, flag):

    if flag["buy_signal"] == 0 and check_candle(data):
            flag["buy_signal"] = 1
            flag["sell_signal"] = 0
    elif flag["buy_signal"] == 1 and check_candle(data) and check_ascend(data, last_data):
            flag["buy_signal"] = 2
    elif flag["buy_signal"] == 2 and check_candle(data) and check_ascend(data, last_data):
            print("3本連続で陽線なので" + str(data["close_price"]) + "で買い指示")

            flag["buy_signal"] = 3
            flag["buy_order"] = True

    elif flag["sell_signal"] == 0 and check_candle_black(data):
            flag["sell_signal"] = 1
            flag["buy_signal"] = 0
    elif flag["sell_signal"] == 1 and check_candle_black(data) and check_acsend_black(data, last_data):
            flag["sell_signal"] = 2
    elif flag["sell_signal"] == 2 and check_candle_black(data) and check_acsend_black(data, last_data):
            print("3本連続で陰線なので" + str(data["close_price"]) + "で売り指示")

            flag["sell_signal"] = 3
            flag["sell_order"] = True

    else:
            flag["buy_signal"] = 0
            flag["sell_signal"] = 0

    return flag


# 手仕舞いのシグナルが出たら決済の成行注文を出す関数
def close_position(data, last_data, flag):

    if flag["BTC_position"] and data["close_price"] < last_data["close_price"]:
         print("前回の終値を下回ったので" + str(data["close_price"]) + "で決済")
         flag["BTC_position"] = False
    elif flag["JPY_position"] and data["close_price"] > last_data["close_price"]:
         print("前回の終値を上回ったので" + str(data["close_price"]) + "で決済")
         flag["JPY_position"] = False

    return flag


# サーバーに出した注文が約定したか確認する関数
def check_buy_order(flag):
     
    # 注文状況を確認して通っていたら以下を実行
	# 一定時間で注文が通っていなければキャンセルする

    flag["buy_order"] = False
    flag["BTC_position"] = True

    return flag


def check_sell_order(flag):
     
    # 注文状況を確認して通っていたら以下を実行
	# 一定時間で注文が通っていなければキャンセルする

    flag["sell_order"] = False
    flag["JPY_position"] = True

    return flag


last_data = get_price(60,0)
print_price(last_data)

flag = {
     "buy_signal" : 0,
     "sell_signal" : 0,
     "buy_order" : False,
     "sell_order" : False,
     "JPY_position" : False,
     "BTC_position" : False
}
i = 1

while i < 500:
    if flag["buy_order"]:
            flag = check_buy_order(flag)
    elif flag["sell_order"]:
            flag = check_sell_order(flag)
    
    data = get_price(60, i)
    if data["close_time"] != last_data["close_time"]:
        print_price(data)

        if flag["BTC_position"] or flag["JPY_position"]:
            flag = close_position(data, last_data, flag)
        else:
            flag = bs_signal(data, last_data, flag)
    
        last_data["close_time"] = data["close_time"]
        last_data["open_price"] = data["open_price"]
        last_data["close_price"] = data["close_price"]
        i += 1

    time.sleep(0)