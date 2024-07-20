import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.layers import LSTM
from tensorflow.keras.models import Sequential

#import os
#os.environ['PYTHONIOENCODING'] = 'utf-8'
#import sys
#sys.stdout.reconfigure(encoding='utf-8')

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

model.save('initial_model.keras') # save model (need to figure out how to be able to re-use the saved model)

previous_100_days = data_training.tail(100) # take previous 100 days

# append previous 100 days to the data_testing, and set as final_df
final_df = pd.concat([previous_100_days, data_testing], ignore_index = True)

# normalize the final dataset
input_data =  scaler.fit_transform(final_df)

# prep test data sequences
x_test = []
y_test = []

# create sequences with 100 timesteps for testing
for i in range(100, input_data.shape[0]):
    x_test.append(input_data[i - 100: i])
    y_test.append(input_data[i, 0])

# convert to numpy
x_test, y_test = np.array(x_test), np.array(y_test)


# generating forecasts (predictions)

y_predicted = model.predict(x_test)

# scale back predicted and actuals to original scale
print(scaler.scale_)
scaler_num = float(scaler.scale_)
print (scaler_num)

# calculate scale factor, rescale the predicted and actuals
scale_factor = 1/scaler_num
y_predicted = y_predicted * scale_factor
y_test = y_test * scale_factor


# plot originals vs predicted prices
plt.figure(figsize = (12,6))
plt.plot(y_test, 'b', label = 'Original Price')
plt.plot(y_predicted, 'r', label = 'Predicted Price')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()