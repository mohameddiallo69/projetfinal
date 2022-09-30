#Import des librairies
import streamlit as st
import pymongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import time
import altair as alt
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

st.set_page_config(
    page_title="Dashboard Analyse de Sentiment",
    page_icon="✅",
    layout="wide",
)

#Titre
st.title("Twitter Analyse de sentiment sur l'Ukraine")
st.markdown("Cette application a pour but de faire une analyse de sentiment sur les tweets concernant la guerre en Ukraine.")

#Sidebar Titre
st.sidebar.title("Sentiment analysis de la guerre en Ukraine")

#Checkbox affichage des donées
if st.checkbox("Afficher les données"):
    st.write(data.head(50))

#Affichage aléatoire de tweets
tweets = st.sidebar.radio('Sentinement', ('Positive', 'Negative', 'Neutral'))
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])
st.write(data.query('sentiment==@tweets')[['text']].sample(1).iat[0,0])

#GroupBy pour compter la répartition
sentiment_group = data.groupby('sentiment').agg({'sentiment': 'count'}).transpose()
total_tweets = len(data['text'])

# Résumé de l'analyse de sentiment
st.subheader('Résumé')
col1, col2, col3 = st.columns(3)
col1.metric("{:.0%}".format(max(sentiment_group.Negative)/total_tweets),"😡 Tweets négatifs")
col2.metric("{:.0%}".format(max(sentiment_group.Neutral)/total_tweets),"😑 Tweets neutres")
col3.metric("{:.0%}".format(max(sentiment_group.Positive)/total_tweets),"😃 Tweets positifs")

#Affichage avec un select de l'analyse de sentiment en histogramme ou digramme circulaire
select = st.sidebar.selectbox('Visualisation des Tweets',['Histogram', 'Pie Chart'], key=1)
sentiments = data['sentiment'].value_counts()
sentiment = pd.DataFrame({'Sentiment':sentiments.index, 'Tweets':sentiments.values})
st.markdown("### Sentiment compteur")
if select == "Histogram":
    fig = px.bar(sentiment, x='Sentiment', y='Tweets', color = 'Tweets', height= 500)
    st.plotly_chart(fig)
else:
    fig = px.pie(sentiment, values='Tweets', names='Sentiment')
    st.plotly_chart(fig)

#Barre qui va se développer pour afficher un tableau de la répartition des sentiment par jour
sentiment_expander = st.expander("Développer pour voir l'analyse de sentiment", expanded=False)
sentiment_bar = alt.Chart(data).mark_bar().encode(
                    x = alt.X('count(id):Q', stack="normalize", axis = alt.Axis(title = 'Pourcentage du Total des Tweets', format='%')),
                    y = alt.Y('monthdate(created_at):O', axis = alt.Axis(title = 'Date')),
                    tooltip = [alt.Tooltip('sentiment', title = 'Sentiment Group'), 'count(id):Q', alt.Tooltip('average(polarity)', title = 'Avg Compound Score'), alt.Tooltip('median(polarity)', title = 'Median Compound Score')],
                    color=alt.Color('sentiment',
                        scale=alt.Scale(
                        domain=['Positive', 'Neutral', 'Negative'],
                        range=['forestgreen', 'lightgray', 'indianred']))
                ).properties(
                    height = 400
                ).interactive()

# Write the chart
sentiment_expander.subheader('Classification du sentiment des Tweets par jour')
sentiment_expander.altair_chart(sentiment_bar, use_container_width=True)

#Affichage d'un nuage de mot
if st.sidebar.checkbox("Afficher un nuage de mot"):
    # Creation d'un dataframe avec une colonne Tweets
    df = pd.DataFrame([tweet for tweet in data.processed_text], columns=['Tweets'])

    # word cloud visualization
    allWords = ' '.join([twts for twts in df['Tweets']])
    wordCloud = WordCloud(width=550, height=300, random_state=21, max_font_size=110).generate(allWords)
    plt.imshow(wordCloud)
    plt.axis('off')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()

# autorefresh
count = st_autorefresh(interval=2500, limit=300)

