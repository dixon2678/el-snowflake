import pyspark
import requests
import os
import snowflake.connector
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark import SparkContext
# JAVA_HOME="/Library/Java/JavaVirtualMachines/adoptopenjdk-8.jdk/Contents/Home"
"""
credentials = "access.json"
jsonFile = open(credentials, 'r')
values = json.load(jsonFile)
jsonFile.close()
"""

os.environ['PYSPARK_PYTHON'] = "/usr/bin/python3"
os.environ['PYSPARK_DRIVER_PYTHON'] = "/usr/bin/python3"

def get_binance_data():
    url = "https://api2.binance.com/api/v3/ticker/24hr"
    response = requests.request("GET", url)
    return response


def process_data():
    json = get_binance_data().json()
    sc =SparkContext()
    spark = SparkSession \
        .builder \
        .appName("Transform Spark Session") \
        .getOrCreate()
    df = spark.read.json(sc.parallelize([json]))
    # Move ticker column to the front
    df = df.select('symbol', 'askPrice', 'askQty', 'bidPrice', 'bidQty', 'closeTime', 'count', 'firstId', 'highPrice', 'lastId', 'lastPrice', 'lastQty', 'lowPrice', 'openPrice', 'openTime', 'prevClosePrice', 'priceChange', 'priceChangePercent', 'quoteVolume', 'volume', 'weightedAvgPrice')
    # Write Data to CSV
    df.toPandas().to_csv('tmpcsv.csv',
                         sep=',',
                         header=True,
                         index=False)

process_data()


 
