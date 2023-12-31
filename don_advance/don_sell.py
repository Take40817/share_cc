import requests
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


#-----設定項目

chart_sec = 3600  # 1時間足を使用
term = 20         # 過去n期間の設定
wait = 0          # ループの待機時間
lot = 1                 # 1トレードの枚数
slippage = 0.0005       # 手数料やスリッページ(0.05%初期値)


#CryptowatchのAPIを使用する関数
def get_price(min, before = 0, after = 0):
        price = []
        params = {"periods" : min }
        if before != 0:
                params["before"] = before
        if after != 0:
                params["after"] = after

        response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc",params)
        data = response.json()

        if data["result"][str(min)] is not None:
                for i in data["result"][str(min)]:
                        if i[1] != 0 and i[2] != 0 and i[3] != 0 and i[4] != 0:
                                price.append({"close_time" : i[0],
                                              "close_time_dt" : datetime.fromtimestamp(i[0]).strftime('%Y/%m/%d %H:%M'),
                                              "open_price" : i[1],
                                              "high_price" : i[2],
                                              "low_price" : i[3],
                                              "close_price": i[4]
                                })
                return price
        
        else:
                print("データが存在しません")
                return None
        

# 時間と始値・終値を表示する関数
def log_price(data, flag):
        log = "時間: " + datetime.fromtimestamp(data["close_time"]).strftime('%Y/%m/%d %H:%M') + " 高値: " + str(data["high_price"]) + " 安値： " + str(data["low_price"]) + "\n"
        flag["records"]["log"].append(log)
        return flag


# ドンチャンブレイクを判定する関数
def donchian(data, last_data):
        highest = max(i["high_price"] for i in last_data)
        if data["high_price"] > highest:
                return {"side" : "BUY", "price" : highest}
        
        lowest = min(i["low_price"] for i in last_data)
        if data["low_price"] < lowest:
                return {"side" : "SELL", "price" : lowest}
        
        return {"side" : None , "price":0}


# ドンチャンブレイクを判定してエントリー注文を出す関数
def entry_signal(data, last_data, flag):
        signal = donchian(data, last_data)
        if signal["side"] == "SELL":
                flag["records"]["log"].append("過去{0}足の最安値{1}円を、直近の安値が{2}円でブレイクしました".format(term, signal["price"], data["low_price"]))
                flag["records"]["log"].append(str(data["close_price"]) + "円で売りの指値注文を出します\n")

                # ここに買い注文のコードを入れる

                flag["order"]["exist"] = True
                flag["order"]["side"] = "SELL"
                flag["order"]["price"] = round(data["close_price"] * lot)

        return flag


# サーバーに出した注文が約定したか確認する関数
def check_order(flag):
	
	    # 注文状況を確認して通っていたら以下を実行
	    # 一定時間で注文が通っていなければキャンセルする
	
        flag["order"]["exist"] = False
        flag["order"]["count"] = 0
        flag["position"]["exist"] = True
        flag["position"]["side"] = flag["order"]["side"]
        flag["position"]["price"] = flag["order"]["price"]
	
        return flag


def close_position(data, last_data, flag):
        
        flag["position"]["count"] += 1
        signal = donchian(data, last_data)

        if flag["position"]["side"] == "SELL":
                if signal["side"] == "BUY":
                        flag["records"]["log"].append("過去{0}足の最高値{1}円を、直近の高値が{2}円でブレイクしました".format(term, signal["price"], data["high_price"]))
                        flag["records"]["log"].append("成行注文を出してポジションを決済します")

                        # 決済の成行注文コードを入れる

                        records(flag, data)
                        flag["position"]["exist"] = False
                        flag["position"]["count"] = 0

        return flag


# 各トレードのパフォーマンスを記録する関数
def records(flag, data):

        # 手仕舞った日時の記録
        flag["records"]["date"].append(data["close_time_dt"])
        
        # 取引手数料等の計算
        entry_price = flag["position"]["price"]
        exit_price = round(data["close_price"] * lot)
        trade_cost = round(exit_price * slippage)
        
        log = "スリッページ・手数料として " + str(trade_cost) + "円を考慮します\n"
        flag["records"]["log"].append(log)
        flag["records"]["slippage"].append(trade_cost)

        # 値幅の計算
        sell_profit = entry_price - exit_price - trade_cost

        # 利益が出てるかの計算
        if flag["position"]["side"] == "SELL":
                flag["records"]["sell-count"] += 1
                flag["records"]["sell-profit"].append(sell_profit)
                flag["records"]["sell-return"].append(round(sell_profit / entry_price * 100, 4))
                flag["records"]["sell-holding-periods"].append(flag["position"]["count"])
                flag["records"]["gross-profit"].append(flag["records"]["gross-profit"][-1] + sell_profit)
                if sell_profit > 0:
                        flag["records"]["sell-winning"] += 1
                        log = str(sell_profit) + "円の利益です\n"
                        flag["records"]["log"].append(log)
                else:
                        log = str(sell_profit) + "円の損失です\n"
                        flag["records"]["log"].append(log)

        return flag


# バックテストの集計用の関数
def backtest(flag):
        
        sell_gross_profit = np.sum(flag["records"]["sell-profit"])
        sell_HP_av = np.average(flag["records"]["sell-holding-periods"])

        print("バックテストの結果")
        print("--------------------------")
        print("売りエントリの成績")
        print("--------------------------")
        print("トレード回数  :  {}回".format(flag["records"]["sell-count"]))
        print("勝率         :  {}%".format(round(flag["records"]["sell-winning"] / flag["records"]["sell-count"] * 100, 1)))
        print("平均リターン  :  {}%".format(round(np.average(flag["records"]["sell-return"]), 4)))
        print("総損益       :  {}円".format(sell_gross_profit))
        print("平均保有期間  :  {}足分".format(round(sell_HP_av, 2)))

        print("--------------------------")
        print("総合の成績")
        print("--------------------------")
        print("総損益       :  {}円".format(sell_gross_profit))
        print("手数料合計    :  {}円".format(np.sum(flag["records"]["slippage"])))

        # ログファイルの出力
        #file =  open("./{0}-log.txt".format(datetime.now().strftime("%Y-%m-%d-%H-%M")),'wt',encoding='utf-8')
        #file.writelines(flag["records"]["log"])


# ------------------------------
# ここからメイン処理
# ------------------------------

price = get_price(chart_sec, after=1483228800)

flag = {
        "order" : {
                "exist" : False,
                "side" : "",
                "price" : 0,
                "count" : 0
        },
        "position" : {
                "exist" : False,
                "side" : "",
                "price" : 0,
                "count" : 0
        },
        "records" : {
                "sell-count" : 0,
                "sell-winning" : 0,
                "sell-return" : [],
                "sell-profit" : [],
                "sell-holding-periods" : [],

                "date" : [],
                "gross-profit" : [0],
                "slippage" : [],
                "log" : []
        }
}

last_data = []
i = 0
while i < len(price):
        
        # ドンチャンの判定に使う過去ｎ足分の安値・高値データを準備する
        if len(last_data) < term:
                last_data.append(price[i])
                flag = log_price(price[i], flag)
                time.sleep(wait)
                i += 1
                continue
        
        data = price[i]
        flag = log_price(data, flag)

        if flag["order"]["exist"]:
                flag = check_order(flag)
        elif flag["position"]["exist"]:
                flag = close_position(data, last_data, flag)
        else:
                flag = entry_signal(data, last_data, flag)

        # 過去データをn個ピッタリに保つために先頭を削除
        del last_data[0]
        last_data.append(data)
        i += 1
        time.sleep(wait)


print("--------------------------")
print("テスト期間：")
print("開始時点 : " + str(price[0]["close_time_dt"]))
print("終了時点 : " + str(price[-1]["close_time_dt"]))
print(str(len(price)) + "件のローソク足データで検証")
print("--------------------------")
print("過去" + str(term) + "期間の最高値を更新したらエントリー")
print("--------------------------")

backtest(flag)

del flag["records"]["gross-profit"][0] # X軸/Y軸のデータ数を揃えるため、先頭の0を削除
date_list = pd.to_datetime(flag["records"]["date"]) # 日付型に変換

plt.plot(date_list, flag["records"]["gross-profit"])
plt.xlabel("Date")
plt.ylabel("Balance")
plt.xticks(rotation = 50)

plt.show()