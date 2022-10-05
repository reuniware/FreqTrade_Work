import os
from datetime import datetime
import ccxt

# retrieve data for the BTC/USDT pair on Binance
binance = ccxt.binance()
ftx = ccxt.gateio()

a = ccxt.exchanges
# for ex in a:
#     #print(ex)
#     exchange_class = getattr(ccxt, ex)
#     #print(exchange_class)
#     exchange = exchange_class()
#     exchange.fetch_tickers()

stop_loop = False

tb = ftx.fetch_tickers()
# tf = ftx.fetch_tickers()

for ex in a:
    # print(ex)
    if ex != "gateio":
        continue
    exchange_class = getattr(ccxt, ex)
    # print(exchange_class)
    exchange = exchange_class()
    try:
        tf = exchange.fetch_tickers()
    except:
        # print(ex, "exception")
        continue

    for lineb in tb.items():
        symbolb = lineb[1]['symbol']
        askb = lineb[1]['ask']
        if symbolb.endswith("/USDT"):
            print("\"" + symbolb + ":USDT\",")
