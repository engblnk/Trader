from kucoin_futures.client import Market, Trade
# https://github.com/Kucoin/kucoin-futures-python-sdk
# https://docs.kucoin.com/futures

import pandas as pd
from datetime import datetime
import apikeys
import logging
from logging.handlers import SocketHandler

class KuCoinAdapter():

    def __init__(self, symbol, leverage):

        self.init_loggger()

        self.symbol = symbol
        self.market = Market(url='https://api-futures.kucoin.com')
        self.trade = Trade(key=apikeys.kucoinKey, secret=apikeys.kucoinSecret, passphrase=apikeys.kucoinPassphrase, is_sandbox=False, url='')
        self.leverage = leverage

    def init_loggger(self):
        self.logger = logging.getLogger('Trader.Exchange.KuCoin')

    def get_historical(self, starttime):
        bar_length = 60
        bars = self.market.get_kline_data(symbol = self.symbol, granularity = bar_length, begin_t = self.timestamp(starttime))
        df = pd.DataFrame(bars)
        return df

    def tick(self):
        currHour = datetime.utcnow().replace(second=0, microsecond=0, minute=0)
        latestBar = self.market.get_kline_data(symbol = self.symbol, granularity = 60)
        self.logger.info(latestBar[-1]) # dirty syntax: list[-1] get the latest element of the array
        df = pd.DataFrame(latestBar)
        return df.tail(1)
    
    def timestamp(self, dt):
        epoch = datetime.utcfromtimestamp(0)
        return int((dt - epoch).total_seconds() * 1000.0) - 1
    
    def get_positionAmt(self):
        response = self.trade.get_position_details(self.symbol)
        self.logger.info(response)
        return(response['currentQty'])
    
    def cancel_all_open_orders(self):
        response = self.trade.cancel_all_limit_order(self.symbol)
        self.logger.info(response)

    def limit_order(self, side, amount, price):
        response = self.trade.create_limit_order(self.symbol, side.lower(), self.leverage, amount, price)
        self.logger.info('limit buy order -> price: ' + str(price) + ' ' + str(response))

    def market_order(self, side, amount):
        response = self.trade.create_market_order(self.symbol, side.lower(), self.leverage, amount)
        self.logger.info(response)
        return(response)

