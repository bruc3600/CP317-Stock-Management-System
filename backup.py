import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Dropout, LSTM, Input
from tensorflow.keras.models import Sequential, load_model
import streamlit as st
from fbprophet import Prophet



#import os
#os.environ['PYTHONIOENCODING'] = 'utf-8'
#import sys
#sys.stdout.reconfigure(encoding='utf-8')

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_db():
    # Set up the MongoDB client and specify the database and collection
    print("Database created")
    client = MongoClient('mongodb://localhost:27017/')  # Adjust the URI as necessary
    db = client['stock_database']
    return db

def save_to_mongo(db, collection_name, data):
    print(f"Inserting data into MongoDB: {data_dict[:5]}")  # Print first 5 records for confirmation
    collection = db[collection_name]
    if isinstance(data, pd.DataFrame):
        # Convert the dataframe to a dictionary and insert it into the collection
        data_dict = data.to_dict("records")
        collection.insert_many(data_dict)
    elif isinstance(data, dict):
        # If data is a single dictionary, insert it directly
        collection.insert_one(data)
    else:
        print("Unsupported data type for MongoDB insertion.")
        
def fetch_and_store_stock_data(ticker, start, end):
    db = get_db()
    data = fetch_stock_data(ticker, start, end)
    if data is not None:
        data = preprocess_data(data)
        save_to_mongo(db, "stock_prices", data)
        return data
    return None

def fetch_stock_data(ticker, start, end):
    try:
        df = yf.download('TSLA', start=start, end=end)  # pull TSLA stock as start point, from specified start to end date
        return df
    except Exception as e:
        print("Failed to fetch data:", e)  # in case of error, print exception rather than crashing.
        return None

# format and create index for values; remove date and Adj Close from value tables
def preprocess_data(df):
    df = df.reset_index()
    df = df.drop(['Date', 'Adj Close'], axis=1)
    return df

def plot_stock_data(df):
    # create moving averages for 100 and 200 days
    mov_avg_100 = df.Close.rolling(100).mean()
    mov_avg_200 = df.Close.rolling(200).mean()

    # create plot
    plt.figure(figsize=(10, 5))
    plt.plot(df['Close'], label='TSLA Close Price')  # plots Closing price, adds label
    plt.plot(mov_avg_100, 'r', label='Moving average 100 days')  # plots MA for 100 days in red
    plt.plot(mov_avg_200, 'm', label='Moving average 200 days')  # plots MA for 200 days in magenta
    # labels
    plt.title('TSLA Stock Close Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Close Price (USD)')
    plt.legend()
    plt.show()  # print plot

def prepare_training_data(df):
    # for ML model
    data_training = pd.DataFrame(df['Close'][0:int(len(df) * 0.70)])  # starts from 0 and goes to 70% of data
    # define training model
    scaler = MinMaxScaler(feature_range=(0, 1))
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
    return x_train, y_train, scaler

def build_and_train_model(x_train, y_train):
    # build the LSTM model
    model = Sequential()
    model.add(Input(shape=(x_train.shape[1], 1)))  # Explicitly define the input shape
    # add first LSTM layer with dropout = 0.2
    model.add(LSTM(units=50, activation='relu', return_sequences=True))
    model.add(Dropout(0.2))

    # add second LSTM layer with dropout = 0.3
    model.add(LSTM(units=60, activation='relu', return_sequences=True))
    model.add(Dropout(0.3))

    # add third LSTM layer with dropout = 0.4
    model.add(LSTM(units=80, activation='relu', return_sequences=True))
    model.add(Dropout(0.4))

    # add fourth LSTM layer with dropout = 0.5
    model.add(LSTM(units=120, activation='relu'))
    model.add(Dropout(0.5))

    model.add(Dense(units=1))  # output layer

    print(model.summary())

    # compile model
    model.compile(optimizer='adam', loss='mean_squared_error')
    # train model
    model.fit(x_train, y_train, epochs=50)

    model.save('initial_model.keras')  # save model
    return model

def load_model_from_file(model_path):
    return load_model(model_path)

def prepare_testing_data(df, scaler):
    data_testing = pd.DataFrame(df['Close'][int(len(df) * 0.70):])  # starts from 70% and until end of data
    previous_100_days = df.tail(100)  # take previous 100 days

    # append previous 100 days to the data_testing, and set as final_df
    final_df = pd.concat([previous_100_days, data_testing], ignore_index=True)

    # normalize the final dataset
    input_data = scaler.fit_transform(final_df)

    # prep test data sequences
    x_test = []
    y_test = []

    # create sequences with 100 timesteps for testing
    for i in range(100, input_data.shape[0]):
        x_test.append(input_data[i - 100: i])
        y_test.append(input_data[i, 0])

    # convert to numpy
    x_test, y_test = np.array(x_test, dtype=np.float32).reshape(-1, 100, 1), np.array(y_test, dtype=np.float32)
    return x_test, y_test

def plot_predictions(y_test, y_predicted):
    # plot originals vs predicted prices
    plt.figure(figsize=(12, 6))
    plt.plot(y_test, 'b', label='Original Price')
    plt.plot(y_predicted, 'r', label='Predicted Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

# store raw data in MongoDB
def store_raw_data_in_mongo(data, ticker):
    records = data.to_dict('records')
    for record in records:
        record['ticker'] = ticker
    collection.insert_many(records)

def main():
    # define timeline for stock pull
    start = '2019-01-01'  # from specified date
    end = datetime.now().strftime('%Y-%m-%d')  # to today's date
    ticker = 'TSLA'
    db = database.get_db()

    df = fetch_stock_data(ticker, start, end)
    if df is not None:
        df = preprocess_data(df)

        #Save to MongoDB
        database.save_to_mongo(db, "stock_prices", df)

        plot_stock_data(df)
        store_raw_data_in_mongo(df, ticker)  # store raw data in MongoDB

        x_train, y_train, scaler = prepare_training_data(df)
        model = build_and_train_model(x_train, y_train)

        # save scaler for future use
        np.save('scaler.npy', scaler.scale_)

        # generating forecasts (predictions)
        x_test, y_test = prepare_testing_data(df, scaler)
        y_predicted = model.predict(x_test)

        # calculate scale factor, rescale the predicted and actuals
        scale_factor = 1 / float(scaler.scale_[0])
        y_predicted = y_predicted * scale_factor
        y_test = y_test * scale_factor

        plot_predictions(y_test, y_predicted)
    else:
        print("Failed to fetch stock data")

main()

#run_model()
#create_site()