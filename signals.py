import streamlit as st
from plotly import graph_objs as go
from prophet import Prophet
import numpy as np
from datetime import datetime

def plot_signals(data, selected_stock):
    data_train = data[['Date', 'Close']]
    data_train = data_train.rename(columns={"Date": "ds", "Close": "y"})

    signal_model = Prophet()
    signal_model.fit(data_train)

    future = signal_model.make_future_dataframe(periods=7)
    future = future[future['ds'] >= datetime.now().strftime('%Y-%m-%d')]
    forecast = signal_model.predict(future)

    forecast['signal'] = np.where(forecast['yhat'].shift(-1) > forecast['yhat'], 'Buy', 'Sell')

    week_forecast = forecast[forecast['ds'] >= datetime.now().strftime('%Y-%m-%d')]

    st.write('Buy/Sell Signals for the Next 7 Days')
    buy_signals = week_forecast[(week_forecast['signal'] == 'Buy')]
    sell_signals = week_forecast[(week_forecast['signal'] == 'Sell')]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
    fig.add_trace(go.Scatter(x=buy_signals['ds'], y=buy_signals['yhat'], mode='markers', name='Buy Signal', marker=dict(color='green', size=10, symbol='triangle-up')))
    fig.add_trace(go.Scatter(x=sell_signals['ds'], y=sell_signals['yhat'], mode='markers', name='Sell Signal', marker=dict(color='red', size=10, symbol='triangle-down')))
    st.plotly_chart(fig)