'''
A simple streamlit app to look at some visualizations for the trades being picked up by the wallet monitor.

Be sure tail_trade.json (or whatever your json file is called) is contained in the same directory.

In your terminal, type: 

    streamlit run 'app_mod.py' 

to boot up the application in your browser
'''

import pandas as pd
import streamlit as st

# Load the JSON file into a DataFrame
df = pd.read_json('tail_trades.json')

# Convert 'timestamp' to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Set up Streamlit page configuration
st.set_page_config(layout="wide")

# Title of the Streamlit app
st.title('Polymarket Trading Bot Trades Analyzer')

# Display number of trades bar graph
st.subheader('Number of Trades')
trade_count = df['proxyWallet'].value_counts()
st.bar_chart(trade_count)

# Display USD size of trades bar graph
st.subheader('USD Size of Trades')
usdc_size = df.groupby('proxyWallet')['usdcSize'].sum()
st.bar_chart(usdc_size)

# Display size of trades over time line graph
st.subheader('Size of Trades Over Time')
df_sorted = df.sort_values('timestamp')
st.line_chart(df_sorted.set_index('timestamp')['size'])

