import snowflake.connector
import pandas as pd
import os
import pyarrow
import fastparquet
from snowflake.connector.pandas_tools import write_pandas
from gcloud import storage
# os.environ["GCLOUD_PROJECT"] = "My First Project"
# os.environ["PROJECT_ROOT"] = "/Users/dix/Desktop/portfolio/el-snowflake"
project_root = os.environ["PROJECT_ROOT"]

# Function to download the tmp csv file from GCS

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client.from_service_account_json(
        '/secret/creds.json')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))

# Main

download_blob("binance_project", "tmpcsv.csv", "finalcsv.csv")
table_name = 'BINANCE_PRICES'
schema = 'PUBLIC'
database = 'BINANCE'

conn = snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        role='SYSADMIN',
    )

# Execute SQL Query to use the correct DB

conn.cursor().execute("USE DATABASE BINANCE")

df = pd.read_csv('finalcsv.csv')

# write_pandas is a functionality from Snowflake connector to directly write pandas df into a table

write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            database=database,
            schema=schema
        )
