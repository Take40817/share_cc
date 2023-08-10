import requests
from datetime import datetime
import time

response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc?periods=60")
data = response.json()

for item in data["result"]["60"]:
	if item[0] == 1691537340:
		print(datetime.fromtimestamp(item[0]).strftime('%Y/%m/%d %H:%M'))
		print(str(item[1]))
		print(str(item[2]))
		print(str(item[3]))
		print(str(item[4]))