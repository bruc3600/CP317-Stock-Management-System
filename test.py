import streamlit as st
import yfinance as yf
from datetime import datetime
from plotly import graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly
import numpy as np
import pandas as pd





#import io
#import sys
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


start = '2019-01-01' # from specified date
end = datetime.now().strftime('%Y-%m-%d') # to todays date

def create_site():
    st.title("Stock Predictor App")
    stocks = ("AAPL", "GOOG", "META", "TSLA", "GME")
    selected_stock = st.selectbox("Select a stock for prediction", stocks)
    n_years = st.slider("Years of prediction:", 1, 4)
    period = n_years * 365
    data_load_state = st.text("Load data...")
    data = fetch_stock_data(selected_stock, start, end)
    data = preprocess_data(data)
    data_load_state.text("Loading data... done!")
    st.subheader("Raw data")
    st.write(data.tail())
    plot_raw_data(data)




@st.cache_data # save data to cache to make faster
def fetch_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end) # pull TSLA stock as start point, from specified start to end date
        return data
    except Exception as e:
        print("Failed to fetch data:", e) # in case of error, print exception rather than crashing.
        return None
    
# format and create index for values; remove date and Adj Close from value tables
def preprocess_data(data):
    data = data.reset_index()
    #data = data.drop(['Date', 'Adj Close'], axis = 1)
    return data

def plot_raw_data(data):
    if data is not None:
        if 'Date' in data.columns:
            figure = go.Figure()
            figure.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open'))
            figure.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
            figure.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True)
            st.plotly_chart(figure)
        else:
            st.error("The 'Date' column is missing from the data")
    else:
        st.error("Data is not available.")




create_site()