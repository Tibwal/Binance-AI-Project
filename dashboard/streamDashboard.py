import streamlit as st
import pymongo
import pandas as pd
import plotly.graph_objects as go
import time
from time import sleep

#App Title
#st.title('your first mongoDB data visualization😎')

# Streamlit app
st.set_page_config(
    page_title='OPA project stream Data dashboard 💰 📈 🚀',
    page_icon='📈',
    layout='wide'
)

Title, image2 = st.columns(2)


@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()

db = client.OPA_MongoDB

@st.cache_data(ttl=10)
def get_btcData():
    collection = db['CandlessticksCollection'].find({})
    return pd.DataFrame(collection)



with Title:
    st.title( 'OPA project stream Data dashboard 💰 📈 🚀')

with image2:
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWNkNXVsNGI4em80ZGFlZnMzb3MyeHB2YnY2OGd4Y2o2ZGlyaHNldSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/nguei03gAsnJzinNto/giphy.gif",
             width=300)


# Retrieve data from Mongodb database
data = get_btcData()
data =data.drop(['_id', 'timestamp','high','low'], axis=1)

# Display data
st.markdown('### Filtered DataFrame')
st.write(data)

# Display candlestick chart
st.markdown('### Candlesticks Chart 📈')
st.line_chart(data,x="date", y="close")                                               
