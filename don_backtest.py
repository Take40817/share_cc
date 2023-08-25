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
        if signal["side"] == "BUY":
                flag["records"]["log"].append("過去{0}足の最高値{1}円を、直近の高値が{2}円でブレイクしました".format(term, signal["price"], data["high_price"]))
                flag["records"]["log"].append(str(data["close_price"]) + "円で買いの指値注文を出します\n")

                # ここに買い注文のコードを入れる

                flag["order"]["exist"] = True
                flag["order"]["side"] = "BUY"
                flag["order"]["price"] = round(data["close_price"] * lot)

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

        if flag["position"]["side"] == "BUY":
                if signal["side"] == "SELL":
                        #print("a")
                        flag["records"]["log"].append("過去{0}足の最安値{1}円を、直近の安値が{2}円でブレイクしました".format(term, signal["price"], data["low_price"]))
                        flag["records"]["log"].append("成行注文を出してポジションを決済します")

                        # 決済の成行注文コードを入れる
                        
                        records(flag, data)
                        flag["position"]["exist"] = False
                        flag["position"]["count"] = 0

                        flag["records"]["log"].append("さらに" + str(data["close_price"]) + "円で売りの指値注文を入れてドテンします")

                        # ここに売り注文のコードを入れる

                        flag["order"]["exist"] = True
                        flag["order"]["side"] = "SELL"
                        flag["order"]["price"] = round(data["close_price"] * lot)

        if flag["position"]["side"] == "SELL":
                if signal["side"] == "BUY":
                        flag["records"]["log"].append("過去{0}足の最高値{1}円を、直近の高値が{2}円でブレイクしました".format(term, signal["price"], data["high_price"]))
                        flag["records"]["log"].append("成行注文を出してポジションを決済します")

                        # 決済の成行注文コードを入れる

                        records(flag, data)
                        flag["position"]["exist"] = False
                        flag["position"]["count"] = 0

                        flag["records"]["log"].append("さらに" + str(data["close_price"]) + "円で買いの指値注文を入れてドテンします")

                        # ここに買い注文のコードを入れる

                        flag["order"]["exist"] = True
                        flag["order"]["side"] = "BUY"
                        flag["order"]["price"] = round(data["close_price"] * lot)

        return flag


# 各トレードのパフォーマンスを記録する関数
def records(flag, data):
        
        # 手仕舞った日時の記録と保有期間を記録
        flag["records"]["date"].append(data["close_time_dt"])
        flag["records"]["holding-periods"].append(flag["position"]["count"])

        # 取引手数料等の計算
        entry_price = flag["position"]["price"]
        exit_price = round(data["close_price"] * lot)
        trade_cost = round(exit_price * slippage)
        
        log = "スリッページ・手数料として " + str(trade_cost) + "円を考慮します\n"
        flag["records"]["log"].append(log)
        flag["records"]["slippage"].append(trade_cost)

        # 値幅の計算
        buy_profit = exit_price - entry_price - trade_cost
        sell_profit = entry_price - exit_price - trade_cost

        # 利益が出てるかの計算
        if flag["position"]["side"] == "BUY":
                flag["records"]["side"].append("BUY")
                flag["records"]["profit"].append(buy_profit)
                flag["records"]["return"].append(round(buy_profit / entry_price * 100, 4))
                if buy_profit > 0:
                        log = str(buy_profit) + "円の利益です\n"
                        flag["records"]["log"].append(log)
                else:
                        log = str(buy_profit) + "円の損失です\n"
                        flag["records"]["log"].append(log)

        if flag["position"]["side"] == "SELL":
                flag["records"]["side"].append("SELL")
                flag["records"]["profit"].append(sell_profit)
                flag["records"]["return"].append(round(sell_profit / entry_price * 100, 4))
                if sell_profit > 0:
                        log = str(sell_profit) + "円の利益です\n"
                        flag["records"]["log"].append(log)
                else:
                        log = str(sell_profit) + "円の損失です\n"
                        flag["records"]["log"].append(log)

        return flag


# バックテストの集計用の関数
def backtest(flag):
        
        # 成績を記録したDataFrameを作成
        records = pd.DataFrame({
                "Date" : pd.to_datetime(flag["records"]["date"]),
                "Profit" : flag["records"]["profit"],
                "Side" : flag["records"]["side"],
                "Rate" : flag["records"]["return"],
                "Periods" : flag["records"]["holding-periods"],
                "Slippage" : flag["records"]["slippage"]
        })

        # 総損益の列を追加する
        records["Gross"] = records.Profit.cumsum()

        # 最大ドローダウンの列を追加する
        records["Drawdown"] = records.Gross.cummax().subtract(records.Gross)
        records["DrawdownRate"] = round(records.Drawdown / records.Gross.cummax() * 100, 1)

        # 買いエントリーと売りエントリーだけをそれぞれ抽出する
        buy_records = records[records.Side.isin(["BUY"])]
        sell_records = records[records.Side.isin(["SELL"])]

        # 月別のデータを集計する
        records["月別集計"] = pd.to_datetime(records.Date.apply(lambda x : x.strftime('%Y/%m')))
        grouped = records.groupby("月別集計")

        month_records = pd.DataFrame({
                "Number" : grouped.Profit.count(),
                "Gross" : grouped.Profit.sum(),
                "Rate" : round(grouped.Rate.mean(), 2),
                "Drawdown" : grouped.Drawdown.max(),
                "Periods" : grouped.Periods.mean()
        })

        print("バックテストの結果")
        print("--------------------------")
        print("買いエントリの成績")
        print("--------------------------")
        print("トレード回数       :  {}回".format(len(buy_records)))
        print("勝率              :  {}％".format(round(len(buy_records[buy_records.Profit > 0]) / len(buy_records) * 100, 1)))
        print("平均リターン       :  {}％".format(round(buy_records.Rate.mean())))
        print("総損益            :  {}円".format(buy_records.Profit.sum()))
        print("平均保有期間       :  {}足分".format(round(buy_records.Periods.mean(), 1)))

        print("--------------------------")
        print("売りエントリの成績")
        print("--------------------------")
        print("トレード回数       :  {}回".format(len(sell_records)))
        print("勝率              :  {}％".format(round(len(sell_records[sell_records.Profit > 0]) / len(sell_records) * 100, 1)))
        print("平均リターン       :  {}％".format(round(sell_records.Rate.mean())))
        print("総損益            :  {}円".format(sell_records.Profit.sum()))
        print("平均保有期間       :  {}足分".format(round(sell_records.Periods.mean(), 1)))

        print("--------------------------")
        print("総合の成績")
        print("--------------------------")
        print("全トレード数       :  {}回".format(len(records) ))
        print("勝率               :  {}％".format(round(len(records[records.Profit>0]) / len(records) * 100, 1)))
        print("平均リターン       :  {}％".format(round(records.Rate.mean(), 2)))
        print("平均保有期間       :  {}足分".format(round(records.Periods.mean(), 1)))
        print("")
        print("最大の勝ちトレード  :  {}円".format(records.Profit.max()))
        print("最大の負けトレード  :  {}円".format(records.Profit.min()))
        print("最大ドローダウン    :  {0}円 / {1}％".format(-1 * records.Drawdown.max(), -1 * records.DrawdownRate.loc[records.Drawdown.idxmax()]))
        print("利益合計           :  {}円".format(records[records.Profit > 0].Profit.sum()))
        print("損失合計           :  {}円".format(records[records.Profit < 0].Profit.sum()))
        print("")
        print("最終損益           :  {}円".format(records.Profit.sum()))
        print("手数料合計         :  {}円".format(-1 * records.Slippage.sum()))

        print("--------------------------")
        print("月別の成績")

        for index, row in month_records.iterrows():
                print("--------------------------")
                print("{0}年{1}月の成績".format(index.year, index.month))
                print("--------------------------")
                print("トレード数         :  {}回".format(row.Number.astype(int)))
                print("月間収益           :  {}円".format(row.Gross.astype(int)))
                print("平均リターン       :  {}％".format(row.Rate))
                print("月間ドローダウン    :  {}円".format(-1 * row.Drawdown.astype(int)))

        # ログファイルの出力
        #file =  open("./{0}-log.txt".format(datetime.now().strftime("%Y-%m-%d-%H-%M")),'wt',encoding='utf-8')
        #file.writelines(flag["records"]["log"])

        # 損益曲線をプロット
        plt.plot(records.Date, records.Gross)
        plt.xlabel("Date")
        plt.ylabel("Balance")
        plt.xticks(rotation = 50)

        plt.show()


# ------------------------------
# ここからメイン処理
# ------------------------------

price = get_price(chart_sec, before = 1688137200, after=1483228800)

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
                "date" : [],
                "profit" : [],
                "return" : [],
                "side" : [],
                "holding-periods" : [],
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

backtest(flag)