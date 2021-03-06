from . import indicator as ind

# Import the backtrader platform
import backtrader as bt

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

class basicStrategy(bt.Strategy):
    params = (
        ('printlog', False),
    )
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
        # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                       'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                       (order.executed.price,
                        order.executed.value,
                        order.executed.comm,),
                        doprint=True)

            else:
                self.log(
                       'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                       (order.executed.price,
                        order.executed.value,
                        order.executed.comm),
                        doprint=True)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                (trade.pnl, trade.pnlcomm), doprint=True)


class myStrategy(basicStrategy):
    params = (
        ('exitbars', 5),
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
        self.ADX_DI = ind.ADX_DI(self.data)
        self.ADX = self.ADX_DI.ADX
        self.DIPlus = self.ADX_DI.DIPlus
        self.DIMinus = self.ADX_DI.DIMinus
        self.DICross = bt.indicators.CrossOver(self.DIPlus, self.DIMinus)
        self.MACD = bt.talib.MACD(self.data)
        self.MACDCross = bt.indicators.CrossOver(self.MACD, 0.0)
    
    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return
        if 1.0 in self.DICross.get(size=5) and (self.ADX[0] - self.ADX[-2]) > 0:
            self.order = self.buy()
        if -1.0 in self.DICross.get(size=5) and (self.ADX[0] - self.ADX[-2]) > 0:
            self.order = self.sell()

class ChipStrategy(basicStrategy):

    def __init__(self):
        self.order = None

        p = 5
        self.dataclose = self.datas[0].close

        self.volume = self.datas[0].volume
        self.volume_ma = bt.indicators.SMA(self.volume, period=p, subplot=True)

        self.FInv = self.datas[0].ForeignInvest
        self.ITrust = self.datas[0].InvestTrust
        self.DInv = self.datas[0].DomInvest
        self.BigChip3 = self.FInv + self.ITrust + self.DInv
        self.BigChip3_ma = bt.indicators.SMA(self.BigChip3, period=p, subplot=True)

    def next(self):
        self.log("BigChip3: {}".format(self.BigChip3[0]), doprint=True)
        if self.order:
            return
        if self.BigChip3_ma[0] > self.volume_ma*0.10:
            self.order = self.buy()
        if self.position:
            if self.BigChip3_ma[0] < 0:
                self.order = self.close()
