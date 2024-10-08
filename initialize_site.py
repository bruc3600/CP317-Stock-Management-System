import streamlit as st
import yfinance as yf
from datetime import datetime
from plotly import graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly
import numpy as np
import pandas as pd
from loginsignupbuttons import buttons, display_page
from site_background import background
from signals import plot_signals
from portfolio import authenticate_user, add_user_to_db, load_user_stocks, add_stock_to_user, remove_stock_from_user


start = '2019-01-01' # from specified date
end = datetime.now().strftime('%Y-%m-%d') # to todays date

def create_site():
    # Custom CSS to change text color to black
    st.markdown("""
        <style>
        del, dfn, em, img, ins, kbd, q, s, samp,
        small, strike, strong, sub, sup, tt, var,
        b, u, i, center,
        dl, dt, dd, ol, ul, li,
        fieldset, form, label, legend,
        table, caption, tbody, tfoot, thead, tr, th, td,
        article, aside, canvas, details, embed,
        figure, figcaption, footer, header, hgroup,        
        section
         {
            color: black !important;
        }
        </style>
        """, unsafe_allow_html=True)
    buttons()  # Handles the display and functionality of login/signup buttons
    display_page()  # Manages what page to display based on login status
    background() # Import background image for website
    
    # Only show the main content if the user is logged in
    if st.session_state.get('logged_in', False):
        email = st.session_state.get('user_email')  # Assumes email is stored in session_state on login
        st.title("Stock Predictor App")
        if 'stocks' not in st.session_state:
            st.session_state.stocks = load_user_stocks(email)

        selected_stock = select_stock(email)

        n_years = st.slider("Years of prediction:", 1, 4)
        period = n_years * 365

        data_load_state = st.text("Loading data...")
        data = fetch_stock_data(selected_stock, start, end)

        if data is not None:
            data = preprocess_data(data)
            data_load_state.text("Loading data... done!")
            symbol = yf.Ticker(selected_stock) # get symbol
            info = symbol.info # download info from yfinance
            stock_name = info.get('longName') # get name of stock
            st.subheader(f"Displaying data for: {selected_stock} - {stock_name}") # display stock symbol & name
            st.subheader("Raw data")
            st.write(data.tail())
            plot_raw_data(data)
            forecast(data, period)
            plot_signals(data, selected_stock)

    else:
        st.title("Please log in to access the Stock Predictor App")

# adds / removes stock from st list, as well as user db
def select_stock(email):
    # add stock
    new_stock = st.text_input("Enter a new stock symbol to add to your portfolio:")
    if st.button("Add stock"):
        if new_stock:
            new_stock = new_stock.strip().upper()
            temp = fetch_stock_data(new_stock, start, end)
            if temp is not None and not temp.empty:
                if new_stock not in st.session_state.stocks:
                    add_stock_to_user(email, new_stock)
                    st.session_state.stocks.append(new_stock)
                    st.success(f"{new_stock} added to your portfolio!")
                else:
                    st.error("Stock already added.")
            else:
                st.error("Please enter a valid stock symbol.")

    # remove stock
    desired_stock = st.text_input("Enter a stock symbol to remove from your portfolio:")
    if st.button("Remove stock"):
        if desired_stock:
            desired_stock = desired_stock.strip().upper()
            if desired_stock in st.session_state.stocks:
                remove_stock_from_user(email, desired_stock)
                st.session_state.stocks.remove(desired_stock)
                st.success(f"{desired_stock} removed from your portfolio!")
            else:
                st.error("Stock not found in your current portfolio.")
            
    selected_stock = st.selectbox("Select a stock for prediction", st.session_state.stocks)
    return selected_stock

# def add_stock_to_list():
#     new_stock = st.session_state.new_stock.strip().upper()
#     if new_stock:
#         temp = fetch_stock_data(new_stock, start, end)
#         if temp is None or temp.empty:
#             st.error("Please enter a valid stock symbol.")
#         elif new_stock and new_stock not in st.session_state.stocks:
#             st.session_state.stocks.append(new_stock)
#             st.success(f"{new_stock} added to the list!")
#         elif new_stock in st.session_state.stocks:
#             st.warning(f"{new_stock} is already in the list!")


@st.cache_data # save data to cache to make faster
def fetch_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end) # pull ticker from specified start to end date
        return data
    except Exception as e:
        print("Failed to fetch data:", e) # in case of error, print exception rather than crashing.
        return None
    
# format and create index for values (instead of date being index)
def preprocess_data(data):
    data = data.reset_index()
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
    st.subheader('Forecast Data Plot')
    forecastfigure1 = plot_plotly(model, forecast) 
    st.plotly_chart(forecastfigure1)

    # plot forecast components
    st.subheader('Forecast components')
    figure2 = model.plot_components(forecast)
    st.write(figure2)   


    pass
# for now this is main function that runs (calls sub functions)