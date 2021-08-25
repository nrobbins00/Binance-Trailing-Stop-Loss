import ccxt
from binance import Binance
import config
import time
from slackerizer import slackhook


# PLEASE CONFIGURE API DETAILS IN config.py

class StopTrail():

    def __init__(self, market, type, stopsize, interval):
        self.binance = Binance(
            api_key=config.API_DETAILS['API_KEY'],
            api_secret=config.API_DETAILS['API_SECRET']
        )
        #print(config.API_DETAILS['API_KEY'], f"      secret {config.API_DETAILS['API_SECRET']}")
        self.slack_webhook = config.API_DETAILS['webhook']
        self.slack_username = config.API_DETAILS['slack_user']
        self.market = market
        self.type = type
        self.stopsize = stopsize
        self.interval = interval
        self.running = False
        self.stoploss = self.initialize_stop()

    def initialize_stop(self):
        if self.type == "buy":
            return (self.binance.get_price(self.market) + self.stopsize)
        elif self.type == "sell_percent":
            return (self.binance.get_price(self.market) * ((100 - self.stopsize) / 100))
        else:
            return (self.binance.get_price(self.market) - self.stopsize)

    def update_stop(self):
        price = self.binance.get_price(self.market)
        if self.type == "sell":
            if (price - self.stopsize) > self.stoploss:
                self.stoploss = price - self.stopsize
                #slackhook(f"New high observed: Updating stop loss to {self.stoploss:.8f}", self.slack_webhook)
                print("New high observed: Updating stop loss to %.8f" % self.stoploss)
            elif price <= self.stoploss:
                self.running = False
                amount = self.binance.get_balance(self.market.split("/")[0])
                price = self.binance.get_price(self.market)
                self.binance.sell(self.market, amount, price)
                slackhook(f"<@{self.slack_username}> Sell triggered | Market price: {price:.8f} | Stop Loss price: {self.stoploss:.8f}", self.slack_webhook)
                print("Sell triggered | Price: %.8f | Stop loss: %.8f" % (price, self.stoploss))
        elif self.type == "sell_percent":
            if (price * ((100 - self.stopsize) / 100)) > self.stoploss:
                self.stoploss = price * ((100 - self.stopsize) / 100)
                #slackhook(f"New high observed: Updating stop loss to {self.stoploss:.8f}", self.slack_webhook)
                print("New high observed: Updating stop loss to %.8f" % self.stoploss)
            elif price <= self.stoploss:
                self.running = False
                amount = self.binance.get_balance(self.market.split("/")[0])
                price = self.binance.get_price(self.market)
                print(amount)
                self.binance.sell(self.market, amount, price)
                slackhook(f"<@{self.slack_username}> Sell triggered | Market price: {price:.8f} | Stop Loss price: {self.stoploss:.8f}", self.slack_webhook)
                print("Sell triggered | Price: %.8f | Stop loss: %.8f" % (price, self.stoploss))
        elif self.type == "buy":
            if (price + self.stopsize) < self.stoploss:
                self.stoploss = price + self.stopsize
                print("New low observed: Updating stop loss to %.8f" % self.stoploss)
            elif price >= self.stoploss:
                self.running = False
                balance = self.binance.get_balance(self.market.split("/")[1])
                price = self.binance.get_price(self.market)
                amount = (balance / price) * 0.99925 # 0.10% maker/taker fee without BNB, 0.075% with BNB
                self.binance.buy(self.market, amount, price)
                slackhook(f"<@{self.slack_username}> Buy triggered | Market price: {price:.8f} | Stop Loss price: {self.stoploss:.8f}", self.slack_webhook)
                print("Buy triggered | Price: %.8f | Stop loss: %.8f" % (price, self.stoploss))
        elif self.type == "buy_percent":
            if (price * ((100 + self.stopsize) / 100)) < self.stoploss:
                self.stoploss = price * ((100 + self.stopsize) / 100)
                print("New low observed: Updating stop loss to %.8f" % self.stoploss)
            elif price >= self.stoploss:
                self.running = False
                balance = self.binance.get_balance(self.market.split("/")[1])
                price = self.binance.get_price(self.market)
                amount = (balance / price) * 0.99925 # 0.10% maker/taker fee without BNB, 0.075% with BNB
                self.binance.buy(self.market, amount, price)
                slackhook(f"<@{self.slack_username}> Buy triggered | Market price: {price:.8f} | Stop Loss price: {self.stoploss:.8f}", self.slack_webhook)
                print("Buy triggered | Price: %.8f | Stop loss: %.8f" % (price, self.stoploss))

    def print_status(self):
        last = self.binance.get_price(self.market)
        print("---------------------")
        print("Trail type: %s" % self.type)
        print("Market: %s" % self.market)
        print("Stop loss: %.8f" % self.stoploss)
        print("Last price: %.8f" % last)
        if self.type == "sell_percent" or "buy_percent":
            print("Stop size percent: %.8f" % self.stopsize)
        else:            
            print("Stop size: %.8f" % self.stopsize)
        print("---------------------")

    def run(self):
        self.running = True
        while (self.running):
            self.print_status()
            self.update_stop()
            time.sleep(self.interval)
