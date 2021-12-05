import pyspark
import requests
import os
import snowflake.connector
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark import SparkContext
from pyspark.sql import functions as F
from gcloud import storage

os.environ["GCLOUD_PROJECT"] = "My First Project"
project_root = os.environ["PROJECT_ROOT"]
def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""

    storage_client = storage.Client.from_service_account_json(
        project_root + '/creds.json')

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)

    return blob.public_url

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
    # Rename Column names to Uppercase
    df = df.select([F.col(x).alias(x.upper()) for x in df.columns])
    df.show()
    # Write Data to CSV
    df.toPandas().to_csv('tmpcsv.csv',
                         sep=',',
                         header=True,
                         index=False)
    
process_data()
upload_to_bucket('tmpcsv.csv', 'tmpcsv.csv', 'binance_project')




 
