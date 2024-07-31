import streamlit as st
from plotly import graph_objs as go
from prophet import Prophet
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def plot_signals(data, selected_stock):

    #Prepare dataframe for intraday analysis
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.set_index('Date')
    data = data.resample('D').ffill().reset_index()

    #Create dataframe
    alert_times = []
    today = datetime.now()
    for i in range(7):
            date = today + timedelta(days=i)
            alert_times.append(date.replace(hour=9, minute = 30))
            alert_times.append(date.replace(hour = 12, minute = 30))
            alert_times.append(date.replace(hour=16, minute = 30))

    alert_df = pd.DataFrame({'ds': alert_times})


    #Set correct format for prophet model
    data_train = data[['Date', 'Close']]
    data_train = data_train.rename(columns={"Date": "ds", "Close": "y"})


    #Initialize model
    signal_model = Prophet()
    signal_model.fit(data_train)


    #Predict dor the next 7 days with specific times
    forecast = signal_model.predict(alert_df)

    #Calculate signals based on price changes
    forecast['signal'] = np.where(forecast['yhat'].shift(-1) > forecast['yhat'], 'Buy', 'Sell')

    #Filter only the next 7 days
    week_forecast = forecast[forecast['ds'] >= datetime.now().strftime('%Y-%m-%d')]

    #Plot Buy/Sell signals
    st.write('Buy/Sell Signals for the Next 7 Days')
    buy_signals = week_forecast[(week_forecast['signal'] == 'Buy')]
    sell_signals = week_forecast[(week_forecast['signal'] == 'Sell')]

    # Visualize Buy/Sell signals
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
    fig.add_trace(go.Scatter(x=buy_signals['ds'], y=buy_signals['yhat'], mode='markers', name='Buy Signal', marker=dict(color='green', size=10, symbol='triangle-up')))
    fig.add_trace(go.Scatter(x=sell_signals['ds'], y=sell_signals['yhat'], mode='markers', name='Sell Signal', marker=dict(color='red', size=10, symbol='triangle-down')))
    st.plotly_chart(fig)