import hashlib
import hmac
import requests
import datetime
import json


api_key = "2fYygqQpc4ruSmMzmdr7LR"
api_secret = "IQ6edS8EInDp5K989rNU9nMiGTVp8dI329T/oomu0iQ="

base_url = "https://api.bitflyer.com"
path_url = "/v1/me/sendchildorder"
method = "POST"

timestamp = str(datetime.datetime.today())

param = {
	"product_code" : "BTC_JPY",
	"child_order_type" : "LIMIT",
	"side" : "BUY",
	"price" : 2800000,
	"size" : 0.01,
}
body = json.dumps(param)

message = timestamp + method + path_url + body
signature = hmac.new(bytearray(api_secret.encode('utf-8')), message.encode('utf-8') , digestmod = hashlib.sha256 ).hexdigest()

headers = {
	'ACCESS-KEY' : api_key,
	'ACCESS-TIMESTAMP' : timestamp,
	'ACCESS-SIGN' : signature,
	'Content-Type' : 'application/json'
}

response = requests.post( base_url + path_url , data = body , headers = headers)
print( response.status_code )
print( response.json() )