import requests
from datetime import datetime
import time

response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc", params = { "periods" : 60 })


def get_price(min, i):

    data = response.json()

    return {"close_time" : data["result"][str(min)][i][0],
            "open_price" : data["result"][str(min)][i][1],
            "high_price" : data["result"][str(min)][i][2],
            "low_price" : data["result"][str(min)][i][3],
            "close_price" : data["result"][str(min)][i][4]}


def print_price(data):
    
    print( "時間： " + datetime.fromtimestamp(data["close_time"]).strftime('%Y/%m/%d %H:%M') + " 始値： " + str(data["open_price"]) + " 終値： " + str(data["close_price"]) )


def check_candle(data, side):

    if data["high_price"] - data["low_price"] == 0: return False
    else:
        realbody_rate = abs(data["close_price"] - data["open_price"]) / (data["high_price"] - data["low_price"])
        increase_rate = data["close_price"] / data["open_price"] - 1

    if side == "buy":
        if data["close_price"] < data["open_price"]: return False
        elif increase_rate < 0.00005: return False
        elif realbody_rate < 0.5: return False
        else: return True

    if side == "sell":
        if data["close_price"] > data["open_price"]: return False
        elif increase_rate > -0.00005: return False
        elif realbody_rate < 0.5: return False
        else: return True


# ローソク足の始値・終値が連続で切りあがってるか確認する関数
def check_ascend(data, last_data):

    if data["open_price"] > last_data["open_price"] and data["close_price"] > last_data["close_price"]:
        return True
    else:
        return False
    

def check_descend(data, last_data):

    if data["open_price"] < last_data["open_price"] and data["close_price"] < last_data["close_price"]:
        return True
    else:
        return False
    

def buy_signal(data, last_data, flag):

    if flag["buy_signal"] == 0 and check_candle(data, "buy"):
        flag["buy_signal"] = 1

    elif flag["buy_signal"] == 1 and check_candle(data, "buy") and check_ascend(data, last_data):
        flag["buy_signal"] = 2

    elif flag["buy_signal"] == 2 and check_candle(data, "buy") and check_ascend(data, last_data):
        print("3本連続で陽線 なので" + str(data["close_price"]) + "で買い指示")
        flag["buy_signal"] = 3

        # ここに買い注文のコードを入れる
        flag["order"]["exist"] = True
        flag["order"]["side"] = "BUY"

    else:
        flag["buy_signal"] = 0

    return flag


def sell_signal(data, last_data, flag):

    if flag["sell_signal"] == 0 and check_candle(data, "sell"):
        flag["sell_signal"] = 1

    elif flag["sell_signal"] == 1 and check_candle(data, "sell") and check_descend(data, last_data):
        flag["sell_signal"] = 2

    elif flag["sell_signal"] == 2 and check_candle(data, "sell") and check_descend(data, last_data):
        print("3本連続で陰線 なので" + str(data["close_price"]) + "で売り指示")
        flag["sell_signal"] = 3
        
        # ここに売り注文のコードを入れる
        flag["order"]["exist"] = True
        flag["order"]["side"] = "SELL"

    else:
        flag["sell_signal"] = 0

    return flag


def close_position(data, last_data, flag):
      
    if flag["position"]["side"] == "BUY":
        if data["close_price"] < last_data["close_price"]:
            print("前回の終値を下回ったので" + str(data["close_price"]) + "あたりで成行で決済します")
            # 成行注文のコードを入れる
            flag["position"]["exist"] = False


    if flag["position"]["side"] == "SELL":
        if data["close_price"] > last_data["close_price"]:
            print("前回の終値を上回ったので" + str(data["close_price"]) + "あたりで成行で決済します")
            # 成行注文のコードを入れる
            flag["position"]["exist"] = False

    return flag  


def check_order(flag):
    
    # 注文状況を確認して通っていたら以下を実行
    # 一定時間で注文が通っていなければキャンセルする

    print("注文が約定しました！")
    flag["order"]["exist"] = False
    flag["order"]["count"] = 0
    flag["position"]["exist"] = True
    flag["position"]["side"] = flag["order"]["side"]
    return flag

# ここからメイン処理
# まずは初期値を取得
last_data = get_price(60, 0)
print_price(last_data)

# 注文管理用フラッグを準備
flag = {
        "buy_signal" : 0,
        "sell_signal" : 0,
        "order" : {
                "exist" : False,
                "side" : "",
                "count" : 0
        },
        "position" : {
                "exist" : False,
                "side" : ""
        }
}

# 注文回数のカウント変数
nt = 0

# 500回のループ処理
i = 1
while i < 1000:
    if flag["order"]["exist"]:
        flag = check_order(flag)
        nt += 1

    data = get_price(60, i)
    print_price(data)

    if flag["position"]["exist"]:
        flag = close_position(data, last_data, flag)
    else:
        flag = buy_signal(data, last_data, flag)
        flag = sell_signal(data, last_data, flag)

    last_data["close_time"] = data["close_time"]
    last_data["open_price"] = data["open_price"]
    last_data["close_price"] = data["close_price"]
    i += 1

print("最終的なテスト回数 : " + str(nt))