import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime

start = '2019-01-01' # from specified date
end = datetime.now().strftime('%Y-%m-%d') # to todays date

try:
    df = yf.download('TSLA', start=start, end=end) # pull TSLA stock as start point, from specified start to end date
except Exception as e:
    print("Failed to fetch data:", e) # in case of error, print exception rather than crashing.
else:
    print(df.tail()) # tail = newer dates, head = older dates

# plot

plt.figure(figsize=(10, 5))
plt.plot(df['Close'], label='TSLA Close Price')
plt.title('TSLA Stock Close Price Over Time')
plt.xlabel('Date')
plt.ylabel('Close Price (USD)')
plt.legend()
plt.show()