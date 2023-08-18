import json
import websocket
from datetime import datetime, timedelta
import dateutil.parser
from logging import getLogger, INFO, StreamHandler
from time import sleep
import csv

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)

TICK_RES = 60

dt_f = datetime.now() + timedelta(seconds = TICK_RES)
tickTs = int(dt_f.timestamp() / TICK_RES) * TICK_RES
dt_s = datetime.fromtimestamp(tickTs)

def get_exec_date(d):
    exec_date = d["exec_date"].replace('T', ' ')[:-1]
    return dateutil.parser.parse(exec_date) + timedelta(hours=9)

class RealtimeAPI(object):
    def __init__(self, url, channel):
        self.url = url
        self.channel = channel
        self.ohlc = {}
        self.ohlc["date"] = ""
        self.now = datetime.now()

        self.csv_file = open("ohlc_data.csv", "w", newline = "")
        self.csv_writer = csv.writer(self.csv_file)
        #self.csv_writer.writerow(["Timestamp", "Date", "Open", "High", "Low", "Close"])

    def run(self):
        while(True):
            self.ws = websocket.WebSocketApp(self.url, header=None, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
            websocket.enableTrace(False)  # データフレームの受信を無効にする
            self.ws.run_forever()
            logger.info('Web Socket process ended. Retrying reconnect')
            sleep(1)

    def on_message(self, ws, message):
        output = json.loads(message)['params']
        for d in output["message"]:
            exec_date = get_exec_date(d)

            if dt_s > exec_date:
                break

            if exec_date < self.now:
                continue

            price = int(d["price"])
            if self.ohlc["date"] != exec_date.strftime("%Y-%m-%d %H:%M"):
                if self.ohlc["date"] != "":
                    # データ出力時刻, 対象ローソク足時刻, Open, High, Low, Close を出力
                    logger.info("{}, {}, 始値: {}, 高値: {}, 低値: {}, 終値: {}"
                                .format(datetime.now(), self.ohlc["date"], self.ohlc["open"], self.ohlc["high"], self.ohlc["low"], self.ohlc["close"]))
                    # CSVファイルに最新のOHLCデータを書き込み
                    self.csv_file.close()  # ファイルを閉じて内容を空にする
                    self.csv_file = open("ohlc_data.csv", "w", newline="")  # 書き込みモードでファイルを開く
                    self.csv_writer = csv.writer(self.csv_file)
                    self.csv_writer.writerow([
                        datetime.now(),
                        self.ohlc["date"],
                        self.ohlc["open"],
                        self.ohlc["high"],
                        self.ohlc["low"],
                        self.ohlc["close"]
                    ])
                    self.csv_file.flush()
                
                self.ohlc["date"] = exec_date.strftime("%Y-%m-%d %H:%M")
                self.ohlc["open"] = price
                self.ohlc["high"] = price
                self.ohlc["low"] = price
                self.ohlc["close"] = price
            else:
                self.ohlc["high"] = max(self.ohlc["high"], price)
                self.ohlc["low"] = min(self.ohlc["low"], price)
                self.ohlc["close"] = price

    def on_error(self, ws, error):
        logger.error(error)

    def on_close(self, ws):
        logger.info('disconnected streaming server')

    def on_open(self, ws):
        #logger.info('connected streaming server')
        output_json = json.dumps(
            {'method': 'subscribe',
             'params': {'channel': self.channel}
             }
        )
        ws.send(output_json)


if __name__ == '__main__':
    url = 'wss://ws.lightstream.bitflyer.com/json-rpc'
    channel = 'lightning_executions_BTC_JPY'
    json_rpc = RealtimeAPI(url=url, channel=channel)
    json_rpc.run()