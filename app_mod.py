# # import pandas as pd
# # import streamlit as st
# # import json
# # from pygwalker.api.streamlit import StreamlitRenderer

# # st.set_page_config(layout="wide")


# # df = pd.read_json('tail_trades.json')

# # # Convert Timestamp columns to strings
# # for column in df.select_dtypes(include=[pd.Timestamp]):
# #     df[column] = df[column].astype(str)

# # st.title('Polymarket Trading Bot Trades Analyzer')

# # pyg_app = StreamlitRenderer(df)
# # pyg_app.explorer()

# # st.write("DataFrame:")
# # st.dataframe(df)

# import pandas as pd
# import streamlit as st
# from pygwalker.api.streamlit import StreamlitRenderer

# st.set_page_config(layout="wide")

# # Load the JSON file into a DataFrame
# df = pd.read_json('tail_trades.json')

# # Convert columns to datetime (if they are not already)
# for column in df.columns:
#     if pd.api.types.is_string_dtype(df[column]):
#         try:
#             df[column] = pd.to_datetime(df[column], errors='ignore')
#         except Exception as e:
#             print(f"Column '{column}' could not be converted to datetime: {e}")

# # Now, convert datetime columns to strings
# for column in df.select_dtypes(include=[pd.Timestamp, 'datetime64[ns]']):
#     df[column] = df[column].astype(str)

# st.title('Polymarket Trading Bot Trades Analyzer')

# pyg_app = StreamlitRenderer(df)
# pyg_app.explorer()

# st.write("DataFrame:")
# st.dataframe(df)


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

