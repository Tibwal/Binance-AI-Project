
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import streamlit as st
import plotly.graph_objects as go
import pymongo
import time
from time import sleep



# Streamlit app
st.set_page_config(
    page_title='OPA project historical and streaming  Data dashboard 💰 📈 🚀',
    page_icon='📈',
    layout='wide'
)

Title, image2 = st.columns(2)


db_connection = st.connection('mysql', type='sql')


def retrieve_data_from_db():
    
    df = db_connection.query('SELECT * FROM history_Data;', ttl=600)
    
    return df

def create_candlestick_chart(df):
    fig = go.Figure(data=[go.Candlestick(x=df['close_time'],
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])
    return fig




with Title:
    st.title( 'OPA project historical and streaming  Data dashboard 💰 📈 🚀')
    
with image2:
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWNkNXVsNGI4em80ZGFlZnMzb3MyeHB2YnY2OGd4Y2o2ZGlyaHNldSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/nguei03gAsnJzinNto/giphy.gif",
             width=300)


# Retrieve data from SQL database
data = retrieve_data_from_db()

# Display data
st.markdown('### Filtered DataFrame')
st.write(data)

# Display candlestick chart
st.markdown('### Candlesticks Chart 📈')
fig = create_candlestick_chart(data)
st.plotly_chart(fig, use_container_width=True)


#########partie streaming
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()

db = client.OPA_MongoDB

@st.cache_data(ttl=10)
def get_btcData():
    collection = db['CandlessticksCollection'].find({})
    return pd.DataFrame(collection)



# Retrieve data from Mongodb database
data_stream = get_btcData()
data_stream =data_stream.drop(['_id', 'timestamp','high','low'], axis=1)

# Display data
st.markdown('### Filtered DataFrame')
st.write(data_stream)

# Display candlestick chart
st.markdown('### streaming Chart 📈')
st.line_chart(data_stream,x="date", y="close")
