import requests
from datetime import datetime
import json


def get_price(min, before = 0, after = 0):
        price = []
        params = {"periods" : min}
        if before != 0:
                params["before"] = before
        if after != 0:
                params["after"] = after

        response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc",params)
        data = response.json()

        if data["result"][str(min)] is not None:
                for i in data["result"][str(min)]:
                        price.append({
                                "close_time" : i[0],
                                "close_time_dt" : datetime.fromtimestamp(i[0]).strftime('%Y/%m/%d %H:%M'),
                                "open_price" : i[1],
                                "high_price" : i[2],
                                "low_price" : i[3],
                                "close_price" : i[4]
                        })
                return price
        
        else:
                print("データが存在しません")
                return None
        

def get_price_from_file(path):
        file = open(path, "r", encoding = "utf-8")
        price = json.load(file)
        return price
        

# ここからメイン
price = get_price(60)
#price = get_price_from_file("./1692004320-1692379560-price.json")
#after=1641006000

if price is not None:
        try:
                print("先頭データ : " + str(price[0]["close_time_dt"]) + "  UNIX時間 : " + str(price[0]["close_time"]))
                print("先頭データ : " + str(price[-1]["close_time_dt"]) + "  UNIX時間 : " + str(price[-1]["close_time"]))
                print("合計 : " + str(len(price)) + "件のローソク足データを取得")
                print("--------------------------")
                print("--------------------------")

                file = open("./{0}-{1}-price.json".format(price[0]["close_time"], price[-1]["close_time"]), "w", encoding = "utf-8")
                json.dump(price, file, indent = 4)

        except Exception as e:
                print('=== エラー内容 ===')
                print('type:' + str(type(e)))
                print('args:' + str(e.args))
                print('e自身:' + str(e))