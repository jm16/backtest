from fetch_data import get_stock_pd
from strategy import basic_strategy
import backtrader as bt

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    stock_pd = get_stock_pd('2454')
    data = bt.feeds.PandasData(
            dataname=stock_pd, 
            volume='transaction'
            )
    
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.addstrategy(basic_strategy)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    cerebro.plot()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
