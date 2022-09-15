import streamlit as st
import pymongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import time
from streamlit_autorefresh import st_autorefresh
from pandas import DataFrame

# Pull data from the collection.

connection = pymongo.MongoClient("mongodb+srv://ProjectFinal_ARMD:PF.password@cluster0.5sajpgx.mongodb.net/?retryWrites=true&w=majority")
db=connection["twitter"]    
collection=db["twitterCol"]

data = DataFrame(list(collection.find()))
data = data.astype({"_id": str})

st.title("Twitter Sentiment Analysis of Ukraine War")
st.markdown("Cette application a pour but de faire une analyse de sentiment sur les tweets concernant la guerre en Ukraine.")

st.sidebar.title("Sentiment analysis de la guerre en Ukraine")

if st.checkbox("Show Data"):
    st.write(data.head(50))

st.sidebar.subheader('Twwets analyse')
tweets = st.sidebar.radio('Sentinement Type', ('Positive', 'Negative', 'Neutral'))
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])


select = st.sidebar.selectbox('Visualisation des Tweets',['Histogram', 'Pie Chart'], key=1)
sentiments = data['sentiment'].value_counts()
sentiment = pd.DataFrame({'Sentiment':sentiments.index, 'Tweets':sentiments.values})
st.markdown("### Sentiment count")
if select == "Histogram":
    fig = px.bar(sentiment, x='Sentiment', y='Tweets', color = 'Tweets', height= 500)
    st.plotly_chart(fig)
else:
    fig = px.pie(sentiment, values='Tweets', names='Sentiment')
    st.plotly_chart(fig)


# Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
# after it's been refreshed 100 times.
count = st_autorefresh(interval=4000, limit=300,)

