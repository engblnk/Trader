from ExchangeFacade import ExchangeFacade
import time
import threading
import logging
from logging.handlers import SocketHandler
import pandas as pd

## KUCOIN FORK EDIP DUZELT
#datefmt="%d/%m/%Y %I:%M:%S %p %Z",

class FuturesTrader():
    def __init__(self, exchangeName, unit):

        self.init_loggger()

        # create exchange Object
        self.exc = ExchangeFacade(exchangeName, leverage = 3)
        self.units = unit
        self.dataSize = 0
        self.pricePresicion = 3
    
    def init_loggger(self):
        self.logger = logging.getLogger('Trader')
        self.logger.setLevel(1)  # to send all records to cutelog
        socket_handler = SocketHandler('127.0.0.1', 19996)  # default listening address
        self.logger.addHandler(socket_handler)
        file_handler = logging.FileHandler('Trader.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def start_trading(self):
        self.data = self.exc.get_historical()

        pollingThread = threading.Thread(target=self.threadedTick)
        pollingThread.start()

    def threadedTick(self):
        while True:
            self.new_bar = self.exc.tick()

            if self.new_bar.tail(1).index[0] in self.data.index:
                self.data.loc[self.new_bar.tail(1).index] = self.new_bar
                logStream = logging.getLogger('Trader.Stream')
                logStream.info('time: ' + str(self.data.tail(1).index[0].hour) 
                                    + ':' + str(self.data.tail(1).index[0].minute).zfill(2)
                                    + ' price: ' + str(self.data.tail(1)['Close'][0]))
            else:
                self.data = pd.concat([self.data, self.new_bar])

            if self.data.size > self.dataSize:
                self.dataSize = self.data.size
                self.define_strategy()
                self.execute_trades()

            # sleep 10 min
            time.sleep(30)
    
    def define_strategy(self):
        
        data = self.data.tail(50).copy()
        
        #******************** define your strategy here ************************
        data = data[["Close"]].copy()
        
        data['EMA21'] = data['Close'].ewm(span=21, min_periods=21, adjust=False).mean()
        data['EMA50'] = data['Close'].ewm(span=50, min_periods=21, adjust=False).mean()

        data.loc[data.EMA21 > data.EMA50, "position"] = 1
        data.loc[data.EMA21 < data.EMA50, "position"] = -1
        #***********************************************************************
        
        self.prepared_data = data.copy()
        logStrategy = logging.getLogger('Trader.Strategy')
        logStrategy.info(self.prepared_data)

    
    def execute_trades(self):

        if self.prepared_data["position"].iloc[-1] == 1:
            orderSide = "BUY"
        elif self.prepared_data["position"].iloc[-1] == -1:
            orderSide = "SELL"

        # Get position Information
        self.positionAmt = self.exc.exchangeObj.get_positionAmt()
        self.logger.info(self.positionAmt)

        # Collect Garbage
        self.exc.exchangeObj.cancel_all_open_orders()
                 
        if (orderSide == "BUY" and self.positionAmt < 0) or (orderSide == "SELL" and self.positionAmt > 0):
            response = self.exc.exchangeObj.market_order(orderSide, abs(self.positionAmt))
            self.logger.info(response)
        
        # Get position Information after Cleaning   
        self.positionAmt = self.exc.exchangeObj.get_positionAmt()
        self.logger.info(self.positionAmt)

        # INVEST
        if abs(self.positionAmt) < self.units:
            self.exc.exchangeObj.limit_order(orderSide, self.units - abs(self.positionAmt), self.roundPrice(self.prepared_data["EMA21"].iloc[-1]))

    def roundPrice(self, price):
        return round(price, self.pricePresicion)

exchangeName = "KuCoin"
unit = 50
trader = FuturesTrader(exchangeName, unit)
trader.start_trading()
