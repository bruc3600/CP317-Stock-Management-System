import streamlit as st
import yfinance as yf
from datetime import datetime
from plotly import graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly
import numpy as np
import pandas as pd
from signals import plot_signals



start = '2019-01-01' # from specified date
end = datetime.now().strftime('%Y-%m-%d') # to todays date

def create_site():
    st.title("Stock Predictor App") # main title
    stocks = ("AAPL", "GOOG", "META", "TSLA", "GME") # current list of stocks, needs updated to dynamic selection
    selected_stock = st.selectbox("Select a stock for prediction", stocks,) 
    n_years = st.slider("Years of prediction:", 1, 4,) # slider provides years for prediction
    period = n_years * 365
    data_load_state = st.text("Load data...")
    data = fetch_stock_data(selected_stock, start, end) # loads data
    data = preprocess_data(data) # resets index (gives date an actual value rather than index)
    data_load_state.text("Loading data... done!")
    st.subheader("Raw data") # header for data
    st.write(data.tail()) # prints tail end of data 
    plot_raw_data(data) # runs plot raw data
    forecast(data, period) # runs prediction model
    plot_signals(data, selected_stock)




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

# plots open and close raw prices
def plot_raw_data(data):
    # to avoid error, ensure there is data to plot
    if data is not None:
        if 'Date' in data.columns:
            figure = go.Figure() # create figure
            figure.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open')) #add trace for 'Open' stock prices
            figure.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close')) # and 'Close' stock prices
            figure.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True) # give figure a title and slider
            st.plotly_chart(figure) # display figure on the front end
        else:
            st.error("The 'Date' column is missing from the data")
    else:
        st.error("Data is not available.")

# generates forecast and displays on front end
def forecast(data, period):
    data_train = data[['Date', 'Close']] # set 'Date' and 'Close' as the columns from the data
    data_train = data_train.rename(columns={"Date": "ds", "Close": "y"}) # rename the columns to match requirements for Prophet
    model = Prophet() # init model
    model.fit(data_train) # fit the model with the training data

    future = model.make_future_dataframe(periods=period) # create dataframe to hold future dates for prediction (using period variable from slider)
    forecast = model.predict(future) # generate predictions for dataframe

    # display on front end
    st.subheader('Forecast data') 
    st.write(forecast.tail()) # shows just the forecast data in table

    # plot forecast data using plotly
    st.write('Forecast Data Plot')
    forecastfigure1 = plot_plotly(model, forecast) 
    st.plotly_chart(forecastfigure1)

    # plot forecast components
    st.write('Forecast components')
    figure2 = model.plot_components(forecast)
    st.write(figure2)



# for now this is main function that runs (calls sub functions)
create_site()