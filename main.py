import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as data
import yfinance as yf
from datetime import datetime

start = '2019-01-01'
end = datetime.now().strftime('%Y-%m-%d')

try:
#    df = data.DataReader('TSLA', 'yahoo', start, end)
    df = yf.download('TSLA', start=start, end=end)
except Exception as e:
    print("Failed to fetch data:", e)
else:
    print(df.tail())