from collections import namedtuple
from pandas import Series, DataFrame
from twstock import Stock
import pandas as pd

from datetime import datetime
import csv
import os.path

database_path = "./database/"
def _get_twstock_online(stock_no="0050", fetch_from=None, save=False):
    S = Stock(stock_no)
    if fetch_from:
        S.fetch_from(fetch_from[0], fetch_from[1])
    if save:
        with open("{}/{}.csv".format(database_path, stock_no), 'w') as f:
            w = csv.writer(f)
            w.writerow(S.data[0]._fields)
            w.writerows(data for data in S.data)
    return S.data

def _get_twstock_local(stock_no="0050"):
    with open("{}/{}.csv".format(database_path, stock_no)) as infile:
        reader = csv.reader(infile)
        Datas = []
        Data = namedtuple("Data", next(reader))
        for data in map(Data._make, reader):
            data = data._replace(date = datetime.strptime(data.date, "%Y-%m-%d %H:%M:%S"))
            Datas.append(data)
        return Datas

def _get_twstock(stock_no="0050", fetch_from=None):
    if os.path.isfile("{}/{}.csv".format(database_path, stock_no)):
        print("local data found!")
        S =  _get_twstock_local(stock_no)
        #  if data too old download it again
        local_datetime = S[-1].date
        now_datetime = datetime.now()
        timedetla = now_datetime - local_datetime
        if timedetla.total_seconds()/3600 > 44:
            print("end date not found, re-fetch online...")
            S = _get_twstock_online(stock_no, fetch_from, save=True)
            return S
        #  if data start date mismatched dowload it again
        if fetch_from:
            start_day = Stock(stock_no).fetch(fetch_from[0], fetch_from[1])[0].date.day
            start_datetime = datetime(fetch_from[0], fetch_from[1], start_day)
            found = 0
            for idx, s in enumerate(S):
                if s.date == start_datetime:
                    found = 1
                    return S[idx:]
            print("start date not found, re-fetch online...")
            S = _get_twstock_online(stock_no, fetch_from, save=True)
            return S

    else:
        print("no local date, fetch online...")
        S = _get_twstock_online(stock_no, fetch_from, save=True)
    return S

def _get_stock_pd_in_day(stock_no="0050", fetch_from=None):
    S = _get_twstock(stock_no, fetch_from)
    keys = list(S[0]._fields)
    S = DataFrame(S, columns=keys)    
    S["weekday"] = S["date"].apply(lambda x: x.date().weekday())
    S = S.set_index("date").apply(pd.to_numeric)
    S["change"] = S["change"] / S["close"].shift(1)
    return S

def _get_stock_pd_in_week(stock_no="0050", fetch_from=None):
    S_day = _get_stock_pd_in_day(stock_no, fetch_from)
    S_week = S_day.resample(
            'W', 
            how=
            {"capacity": 'sum',
             "turnover": 'sum',   
             "open": 'first',   
             "high": 'max',
             "low": 'min',
             "close": 'last',
             "change": 'sum',
             "transaction": 'sum'
            })
    S_week = S_week.dropna()
    return S_week

def _get_stock_pd_in_month(stock_no="0050", fetch_from=None):
    S_day = _get_stock_pd_in_day(stock_no, fetch_from)
    S_month = S_day.resample(
            'M', 
            how=
            {"capacity": 'sum',
             "turnover": 'sum',   
             "open": 'first',   
             "high": 'max',
             "low": 'min',
             "close": 'last',
             "change": 'sum',
             "transaction": 'sum'
            })
    S_month = S_month.dropna()
    return S_month


def get_stock_pd(stock_no="0050", fetch_from=None, scale="day"):
    if scale == "day":
        return _get_stock_pd_in_day(stock_no, fetch_from)
    if scale == "week":
        return _get_stock_pd_in_week(stock_no, fetch_from)
    if scale == "month":
        return _get_stock_pd_in_month(stock_no, fetch_from)

