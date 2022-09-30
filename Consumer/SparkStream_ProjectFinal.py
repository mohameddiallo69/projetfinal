
#import des librairies
from pyspark.sql import functions as F
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.types import StringType, StructType, StructField, FloatType, IntegerType
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
import re
import pymongo
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#Spark session
spark = SparkSession \
        .builder \
        .master("spark://spark-master:7077")\
        .appName("ProjectFinal_AnalysisSentiment") \
        .config("spark.mongodb.input.uri", "mongodb://ProjectFinal_ARMD:PF.password@mongo:27017")\
        .config("spark.mongodb.output.uri", "mongodb://ProjectFinal_ARMD:PF.password@mongo:27017")\
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .getOrCreate()
        
#Spark readStream
df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "ARMD_ProjectFinal") \
        .option("startingOffsets", "latest") \
        .load()

# COMMAND ----------

#Schema & transformation
mySchema = StructType([StructField("id", StringType(), True),
                     StructField("created_at", StringType(), True),
                     StructField("text", StringType(), True)])

values = df.select(from_json(df.value.cast("string"), mySchema).alias("tweet"))

# COMMAND ----------

#Fonction qui va nettoyer les tweets
def cleanTweet(tweet: str) -> str:
    tweet = re.sub(r'http\S+', '', str(tweet))
    tweet = re.sub(r'bit.ly/\S+', '', str(tweet))
    tweet = tweet.strip('[link]')

    # retire les users
    tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))
    tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))

    # retire la punctuation
    my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@â'
    tweet = re.sub('[' + my_punctuation + ']+', ' ', str(tweet))

    # retire les nombres
    tweet = re.sub('([0-9]+)', '', str(tweet))

    # retire les hashtag
    tweet = re.sub('(#[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))

    return tweet

#Nettoyage des tweets + ajout d'une colonne avec les tweets nettoyés
df1 = values.select("tweet.*")
clean_tweets = F.udf(cleanTweet, StringType())
raw_tweets = df1.withColumn('processed_text', clean_tweets(col("text")))


#Fonction de polarité
def getPolarity(tweet: str) -> float:
    sid_obj = SentimentIntensityAnalyzer()
    return sid_obj.polarity_scores(tweet)["compound"]

#Fonction de sentiment
def getSentiment(polarityValue: float) -> str:
    if polarityValue >= 0.05 :
        return 'Positive'
    elif polarityValue <= - 0.05 :
        return 'Negative'
    else:
        return 'Neutral'

# COMMAND ----------

#Ajout des colonnes avec le résultats des fonctions de subjectivité, polarité, sentiment
polarity = F.udf(getPolarity, FloatType())
sentiment = F.udf(getSentiment, StringType())

polarity_tweets = raw_tweets.withColumn("polarity", polarity(col("processed_text")))
sentiment_tweets = polarity_tweets.withColumn("sentiment", sentiment(col("polarity")))

# COMMAND ----------

#Classe qui va envoyer les données vers MongoDB
class WriteRowMongo:
    def open(self, partition_id, epoch_id):
        self.myclient = pymongo.MongoClient("mongodb://ProjectFinal_ARMD:PF.password@mongo:27017")
        self.mydb = self.myclient["twitter"]
        self.mycol = self.mydb["twitterCol"]
        return True

    def process(self, row):
        self.mycol.insert_one(row.asDict())

    def close(self, error):
        self.myclient.close()
        return True
    
    

# COMMAND ----------

#Envoie des données vers MongoDB
query = sentiment_tweets.writeStream.foreach(WriteRowMongo()).start().awaitTermination()

# COMMAND ----------


