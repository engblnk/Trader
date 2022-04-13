
import apikeys
from binance.client import Client
import pandas as pd

class BinanceAdapter():
    def __init__(self, symbol, leverage):
        self.symbol = symbol
        self.client = Client(api_key = apikeys.api_key, api_secret = apikeys.secret_key, tld = "com")
        self.client.futures_change_leverage(symbol = self.symbol, leverage = leverage) # NEW

    def get_historical(self, starttime):
        bar_length = "1h"
        bars = self.client.futures_historical_klines(symbol = self.symbol, interval = bar_length,
        start_str = str(starttime), end_str = None, limit = 2)
        df = pd.DataFrame(bars)
        df.drop(df.columns[[6,7,8,9,10,11]],axis=1,inplace=True)
        return df
