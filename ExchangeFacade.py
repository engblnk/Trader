from datetime import timedelta, datetime
from BinanceAdapter import BinanceAdapter
from KuCoinAdapter import KuCoinAdapter
import pandas as pd
import logging
from logging.handlers import SocketHandler

class ExchangeFacade():
    def __init__(self, exchangeName, leverage):

        self.init_loggger()

        self.exchangeName = exchangeName
        if self.exchangeName == "Binance":
            self.exchangeObj = BinanceAdapter(symbol = 'CRVUSDT', leverage = leverage)
        elif self.exchangeName == "KuCoin":
            self.exchangeObj = KuCoinAdapter(symbol = 'CRVUSDTM', leverage = leverage)

    def init_loggger(self):
        self.logger = logging.getLogger('Trader.Exchange')
        self.logger.setLevel(1)  # to send all records to cutelog
        file_handler = logging.FileHandler('Exchange.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_historical(self):
        now = datetime.utcnow()
        past = now - timedelta(days = 2)
        df = self.exchangeObj.get_historical(starttime = past)
        return self.formatColumns(df)

    def tick(self):
        df = self.exchangeObj.tick()
        return self.formatColumns(df)

    def formatColumns(self, df):
        df["Date"] = pd.to_datetime(df.iloc[:,0], unit = "ms")
        df.set_index("Date", inplace = True)
        for column in df.columns:
            df[column] = pd.to_numeric(df[column], errors = "coerce")

        df.columns = ["OpenTime", "Open", "High", "Low", "Close", "Volume"]
        df = df.drop(["OpenTime"], axis=1)
        return df
    
    def get_positionAmt(self):
        positionAmt = self.exchangeObj.get_positionAmt()
        self.logger.info("Position Amount: ", self.positionAmt)

    



