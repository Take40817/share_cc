from datetime import datetime
import json

MIN = 5

def proccessing_datetime(new_price):
        ohlc = []
        index = 0
        
        if price:
                
                for ind, val in enumerate(new_price):
                        dt_min = int(datetime.fromtimestamp(val["close_time"]).strftime('%M'))
                        if dt_min %MIN == 1:
                                break

                for i in new_price[ind:]:
                        dt_min = int(datetime.fromtimestamp(i["close_time"]).strftime('%M'))
                        if dt_min %MIN == 1:
                                ohlc.append({
                                        "close_time" : i["close_time"],
                                        "close_time_dt" : i["close_time_dt"],
                                        "open_price" : i["open_price"],
                                        "high_price" : i["high_price"],
                                        "low_price" : i["low_price"],
                                        "close_price" : i["close_price"]
                                })
                                index += 1
                        else:
                                c = ohlc[(index-1)]
                                c["close_time"] = i["close_time"]
                                c["close_time_dt"] = i["close_time_dt"]
                                c["high_price"] = max(c["high_price"], i["high_price"])
                                c["low_price"] = min(c["low_price"], i["low_price"])
                                c["close_price"] = i["close_price"]
                                
                return ohlc
                

def get_price_from_file(path):
        file = open(path, "r", encoding = "utf-8")
        price = json.load(file)
        return price


def delete_data(price):
        index_time = []
        new_price = []

        for index, value in enumerate(price):
                time = int(datetime.fromtimestamp(value["close_time"]).strftime('%M'))
                if time %MIN == 0:
                        index_time.append(index)

        for i in price[:index_time[-1] + 1]:
                new_price.append({
                                "close_time" : i["close_time"],
                                "close_time_dt" : i["close_time_dt"],
                                "open_price" : i["open_price"],
                                "high_price" : i["high_price"],
                                "low_price" : i["low_price"],
                                "close_price" : i["close_price"]
                })
    
        return new_price


# main
price = get_price_from_file("./1692004320-1692379560-price.json")
new_price = delete_data(price)
ohlc = proccessing_datetime(new_price)

if ohlc is not None:
        try:
                print("先頭データ : " + str(ohlc[0]["close_time_dt"]) + "  UNIX時間 : " + str(ohlc[0]["close_time"]))
                print("先頭データ : " + str(ohlc[-1]["close_time_dt"]) + "  UNIX時間 : " + str(ohlc[-1]["close_time"]))
                print("合計 : " + str(len(ohlc)) + "件のローソク足データを取得")
                print("--------------------------")
                print("--------------------------")

                #file = open("./{0}-{1}-price.json".format(price[0]["close_time"], price[-1]["close_time"]), "w", encoding = "utf-8")
                #json.dump(price, file, indent = 4)

        except Exception as e:
                print('=== エラー内容 ===')
                print('type:' + str(type(e)))
                print('args:' + str(e.args))
                print('e自身:' + str(e))

# for i in ohlc:
#         print(i["close_time_dt"])