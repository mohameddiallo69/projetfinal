#Import des librairies
import streamlit as st
import pymongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import time
from datetime import datetime
from datetime import date
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
from pandas import DataFrame

#date d'aujourd'hui
today = date.today()

# Récupère les donénes depuis la collection de MongoDB
connection = pymongo.MongoClient("mongodb://ProjectFinal_ARMD:PF.password@mongo:27017")
db=connection["twitter"]    
collection=db["twitterCol"]

#Transforme les données
data = DataFrame(list(collection.find()))
data = data.astype({"_id": str})
data = data.drop(columns='_id')

#Titre
st.title("Twitter Sentiment Analysis of Ukraine War")
st.markdown("Cette application a pour but de faire une analyse de sentiment sur les tweets concernant la guerre en Ukraine.")

#Sidebar Titre
st.sidebar.title("Sentiment analysis de la guerre en Ukraine")

#Checkbox affichage des donées
if st.checkbox("Afficher les données"):
    st.write(data.head(50))

#Affichage aléatoire de tweets
tweets = st.sidebar.radio('Sentinement Type', ('Positive', 'Negative', 'Neutral'))
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])

#Affichage avec un select de l'analyse de sentiment en histogramme ou digramme circulaire
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

#Affichage d'un nuage de mot
if st.sidebar.checkbox("Afficher un nuage de mot"):
    # Creation d'un dataframe avec une colonne Tweets
    df = pd.DataFrame([tweet for tweet in data.processed_text], columns=['Tweets'])
    # word cloud visualization
    allWords = ' '.join([twts for twts in df['Tweets']])
    #wordCloud = WordCloud(width=300, height=200, random_state=21, max_font_size=110).generate(allWords)
    #plt.imshow(wordCloud, interpolation="bilinear")
    #plt.axis('off')
    #plt.savefig('WC.jpg')
    #img= Image.open("WC.jpg") 
    wordCloud = WordCloud().generate(allWords)
    plt.imshow(wordCloud)
    plt.axis('off')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    
    #st.image(img)


# Run the autorefresh about every 2500 milliseconds (2.5 seconds) and stop
# after it's been refreshed 300 times.
count = st_autorefresh(interval=2500, limit=300)

