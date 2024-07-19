import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.python.keras.layers import Dense, Dropout
from tensorflow.python.keras.layers.recurrent import LSTM
from tensorflow.python.keras.models import Sequential


# define timeline for stock pull
start = '2019-01-01' # from specified date
end = datetime.now().strftime('%Y-%m-%d') # to todays date

# pull TSLA stock (as example for now)
try:
    df = yf.download('TSLA', start=start, end=end) # pull TSLA stock as start point, from specified start to end date
except Exception as e:
    print("Failed to fetch data:", e) # in case of error, print exception rather than crashing.
else:
    print(df.tail()) # tail = newer dates, head = older dates

# format and create index for values; remove date and Adj Close from value tables
df = df.reset_index()
df = df.drop(['Date', 'Adj Close'], axis = 1)
print (df.head())


# create moving averages for 100 and 200 days
mov_avg_100 = df.Close.rolling(100).mean()
mov_avg_200 = df.Close.rolling(200).mean()

# create plot
plt.figure(figsize=(10, 5))
plt.plot(df['Close'], label='TSLA Close Price') # plots Closing price, adds label
plt.plot(mov_avg_100, 'r', label='Moving average 100 days') # plots MA for 100 days in red
plt.plot(mov_avg_200, 'm', label='Moving average 200 days') # plots MA for 200 days in magenta
# labels
plt.title('TSLA Stock Close Price Over Time')
plt.xlabel('Date')
plt.ylabel('Close Price (USD)')
plt.legend()
plt.show() # print plot


# for ML model
data_training = pd.DataFrame(df['Close'][0:int(len(df)*0.70)]) # starts from 0 and goes to 70% of data
data_testing = pd.DataFrame(df['Close'][int(len(df)*0.70): int(len(df))]) # starts from 70% and until end of data

# define training model
scaler = MinMaxScaler(feature_range=(0,1))
data_training_array = scaler.fit_transform(data_training)

# preparing training data
x_train = []
y_train = []

# create data structure with 100 timesteps and 1 output
for i in range(100, data_training_array.shape[0]):
    x_train.append(data_training_array[i - 100: i])
    y_train.append(data_training_array[i, 0])

# convert to numpy arrays
x_train, y_train = np.array(x_train, dtype=np.float32).reshape(-1, 100, 1), np.array(y_train, dtype=np.float32)


# build the LSTM model
model = Sequential()

# add first LSTM layer with dropout = 0.2
model.add(LSTM(units = 50, activation = 'relu', return_sequences = True, input_shape = (x_train.shape[1], 1)))
model.add(Dropout(0.2))


# add second LSTM layer with dropout = 0.3
model.add(LSTM(units = 60, activation = 'relu', return_sequences = True))
model.add(Dropout(0.3))


# add third LSTM layer with dropout = 0.4
model.add(LSTM(units = 80, activation = 'relu', return_sequences = True))
model.add(Dropout(0.4))


# add fourth LSTM layer with dropout = 0.5
model.add(LSTM(units = 120, activation = 'relu'))
model.add(Dropout(0.5))

model.add(Dense(units = 1)) # output layer

print(model.summary())

# compile model
model.compile(optimizer='adam', loss = 'mean_squared_error')
# train model
model.fit(x_train, y_train, epochs = 50)