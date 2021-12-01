import pyspark
import requests
from pyspark.sql import SparkSession
from pyspark import SparkContext

def get_binance_data():
    url = "https://api2.binance.com/api/v3/ticker/24hr"
    response = requests.request("GET", url)
    return response


json = get_binance_data().json()
sc =SparkContext()
spark = SparkSession \
    .builder \
    .appName("EL Spark Session") \
    .getOrCreate()

df = spark.read.json(sc.parallelize([json]))
df.show()

