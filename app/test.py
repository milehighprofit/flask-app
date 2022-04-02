import datetime as dt
import requests
import pandas as pd
import numpy as np
import matplotlib
import mplfinance as mpf
import talib

def now(lookback):
    #get time now convert it to unix
    timenow = dt.datetime.utcnow()
    end_time = timenow.replace(tzinfo=dt.timezone.utc).timestamp()
    #get lookback and convert to unix
    start_time = dt.datetime.utcnow() - dt.timedelta(lookback)
    start_time = start_time.replace(tzinfo=dt.timezone.utc).timestamp()
    return start_time, end_time


def getmarkets(PERP):
    markets = requests.get(f"https://ftx.com/api/markets").json()
    markets = pd.DataFrame(markets['result'])
    markets = markets['name'].tolist()
    markets = [market for market in markets if market.endswith(PERP)]
    return markets

perpnames = getmarkets('PERP')

def ohlc(perpnames, tf, daysback):
    _start_time, _end_time = now(daysback)
    data = requests.get(f"https://ftx.com/api//markets/{perpnames}/candles?resolution={tf}&start_time={_start_time}&end_time={_end_time}").json()
    data = pd.DataFrame(data['result'])
    return data

dfs = []
tf = 14400
daysback = 10
for perp in perpnames:
    dfs.append(ohlc(perp, tf, daysback))


nameless = pd.concat(dfs, axis=1)
closes = nameless.loc[:,nameless.columns.get_level_values(0).isin(['close'])]


def divs(closes, columns, ob=50, os=50, period=14):
    """Calculates bullish and bearish RSI divergences under oversold or overbought conditions"""

    closes['RSI'] = talib.RSI(closes.iloc[:, columns])
    closes['rolling_rsi_high'] = closes['RSI'].rolling(period).max()
    closes['rolling_rsi_low'] = closes['RSI'].rolling(period).min()
    closes['rolling_closing_high'] = closes.iloc[:, columns].rolling(period).max()
    closes['rolling_closing_low'] = closes.iloc[:, columns].rolling(period).min()


    closes['new_RSI_high'] = np.where(closes['rolling_rsi_high'] > closes['rolling_rsi_high'].shift(), 1, 0)
    closes['new_RSI_low'] = np.where(closes['rolling_rsi_low'] < closes['rolling_rsi_low'].shift(), 1, 0)


    closes['new_closing_high'] = np.where(closes['rolling_closing_high'] > closes['rolling_closing_high'].shift(), 1, 0)
    closes['new_closing_low'] = np.where(closes['rolling_closing_low'] < closes['rolling_closing_low'].shift(), 1, 0)

    closes['bearish_rsi_div'] = np.where((closes['new_closing_high'] == 1) & (closes['new_RSI_high'] == 0) & (closes['RSI'] > ob), 1, 0)
    closes['bullish_rsi_div'] = np.where((closes['new_closing_low'] == 1) & (closes['new_RSI_low'] == 0) & (closes['RSI'] < os), 1, 0)
    closes = closes.dropna()
    return closes[['bullish_rsi_div', 'bearish_rsi_div']]


rsidata = []
for column in range(179):
    results = divs(closes, column)
    if not results.empty:
        rsidata.append(results)
alle = pd.concat(dict(zip(perpnames,rsidata)), axis=1)

cols = (alle.iloc[-3:] != 0).any()
websitedata = alle.iloc[-3:][cols[cols].index]

print(websitedata)