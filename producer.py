#Import des librairies
import json
from kafka import KafkaProducer
from sys import api_version
from tweepy import StreamingClient, StreamRule
import datetime
import time
import auth_tokens as auth
import tweepy


producer = KafkaProducer(bootstrap_servers=['51.38.185.58:9092'], api_version=(2, 0, 2), value_serializer=lambda t: json.dumps(t, default=str).encode("utf-8"),)

topic_name = 'ARMD_ProjectFinal'

class TweetPrinterV2(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(f"{tweet.id} {tweet.created_at} {tweet.text} {tweet.author_id}")
        data = tweet.data
        data["id"] = (tweet.id)
        data["created_at"] = str(tweet.created_at)
        producer.send(topic_name, data)
        #print("-" * 50)

printer = TweetPrinterV2("AAAAAAAAAAAAAAAAAAAAALxOgwEAAAAAo8zDrN%2BFybjVGe1yBCNkkbOCgdo%3DzA7NRr87pj4saKbJaYfJIyktLrfyBNBIHs7CFmlGTXjkX5A6F8")

# add new rules
rule = StreamRule(value="ukraine lang:en")
printer.add_rules(rule)

printer.filter(tweet_fields="created_at", expansions = ['author_id'])

