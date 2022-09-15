# Databricks notebook source
# MAGIC %sh pip install textblob

# COMMAND ----------

pip install pymongo[srv]

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.types import StringType, StructType, StructField, FloatType
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.ml.feature import RegexTokenizer
import re
from textblob import TextBlob
import pymongo

#spark = SparkSession.builder \
#        .appName("ProjectFinal_AnalysisSentiment") \
#        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
#        .getOrCreate()

spark = SparkSession \
        .builder \
        .appName("ProjectFinal_AnalysisSentiment") \
        .config("spark.mongodb.input.uri",\
                "mongodb+srv://ProjectFinal_ARMD:PF.password@cluster0.5sajpgx.mongodb.net/?retryWrites=true&w=majority")\
        .config("spark.mongodb.output.uri",\
                "mongodb+srv://ProjectFinal_ARMD:PF.password@cluster0.5sajpgx.mongodb.net/?retryWrites=true&w=majority")\
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .getOrCreate()

df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "51.38.185.58:9092") \
        .option("subscribe", "ARMD_ProjectFinal") \
        .option("startingOffsets", "latest") \
        .load()

# COMMAND ----------

mySchema = StructType([StructField("text", StringType(), True)])
    # Get only the "text" from the information we receive from Kafka. The text is the tweet produce by a user
values = df.select(from_json(df.value.cast("string"), mySchema).alias("tweet"))

# COMMAND ----------

def cleanTweet(tweet: str) -> str:
    tweet = re.sub(r'http\S+', '', str(tweet))
    tweet = re.sub(r'bit.ly/\S+', '', str(tweet))
    tweet = tweet.strip('[link]')

    # remove users
    tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))
    tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))

    # remove puntuation
    my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@â'
    tweet = re.sub('[' + my_punctuation + ']+', ' ', str(tweet))

    # remove number
    tweet = re.sub('([0-9]+)', '', str(tweet))

    # remove hashtag
    tweet = re.sub('(#[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))

    return tweet

# COMMAND ----------

df1 = values.select("tweet.*")
clean_tweets = F.udf(cleanTweet, StringType())
raw_tweets = df1.withColumn('processed_text', clean_tweets(col("text")))

# COMMAND ----------

def getSubjectivity(tweet: str) -> float:
    return TextBlob(tweet).sentiment.subjectivity


# Create a function to get the polarity
def getPolarity(tweet: str) -> float:
    return TextBlob(tweet).sentiment.polarity


def getSentiment(polarityValue: int) -> str:
    if polarityValue < 0:
        return 'Negative'
    elif polarityValue == 0:
        return 'Neutral'
    else:
        return 'Positive'

# COMMAND ----------

subjectivity = F.udf(getSubjectivity, FloatType())
polarity = F.udf(getPolarity, FloatType())
sentiment = F.udf(getSentiment, StringType())

subjectivity_tweets = raw_tweets.withColumn('subjectivity', subjectivity(col("processed_text")))
polarity_tweets = subjectivity_tweets.withColumn("polarity", polarity(col("processed_text")))
sentiment_tweets = polarity_tweets.withColumn("sentiment", sentiment(col("polarity")))

# COMMAND ----------

rawData = sentiment_tweets\
    .writeStream\
    .outputMode("append")\
    .format("memory")\
    .queryName("rawData").start()

# COMMAND ----------

rawData.status

# COMMAND ----------

display(spark.sql("select * from rawData"))

# COMMAND ----------

def write_row_in_mongo(df, epoch_id):
    mongoURL = "mongodb+srv://ProjectFinal_ARMD:PF.password@cluster0.5sajpgx.mongodb.net/ProjectFinal_ARMD.UkraineWarTweets"
    df.write.format("mongo").mode("append").option("uri", mongoURL).save()
    pass

# COMMAND ----------

class WriteRowMongo:
    def open(self, partition_id, epoch_id):
        self.myclient = pymongo.MongoClient("mongodb+srv://ProjectFinal_ARMD:PF.password@cluster0.5sajpgx.mongodb.net/?retryWrites=true&w=majority")
        self.mydb = self.myclient["twitter"]
        self.mycol = self.mydb["twitterCol"]
        return True

    def process(self, row):
        self.mycol.insert_one(row.asDict())

    def close(self, error):
        self.myclient.close()
        return True
    
    

# COMMAND ----------

query = sentiment_tweets.writeStream.foreach(WriteRowMongo()).start().awaitTermination()

# COMMAND ----------

# MAGIC %sh ifconfig

# COMMAND ----------


