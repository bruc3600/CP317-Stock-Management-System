import streamlit as st
import yfinance as yf
from datetime import datetime
from plotly import graph_objs as go


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
    data_load_state.text("Loading data... done!")
    st.subheader("Raw data")
    st.write(data.tail())




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

def plot_raw_data():








create_site()