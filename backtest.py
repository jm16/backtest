from fetch_data import get_stock_pd
from strategy import myStrategy
import backtrader as bt
import sys


class PandasData_basic(bt.feeds.PandasData):
    lines=('change',)
    params = (('change', 8),)

class PandasData_withchip(PandasData_basic):
    lines=('DomInvest', 'InvestTrust', 'ForeignInvest')
    params = (('DomInvest', 9), ('InvestTrust', 10), ('ForeignInvest', 11))


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    stock_pd = get_stock_pd(sys.argv[1], fetch_from=(2015, 1), scale="day")
    data = PandasData_basic(
            dataname=stock_pd, 
            volume='capacity',
            change='change'
            )
    
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
    cerebro.broker.setcommission(commission=0.003)
    cerebro.addstrategy(myStrategy)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    #  cerebro.plot()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
