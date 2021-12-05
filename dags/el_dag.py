from datetime import timedelta
from textwrap import dedent
from airflow.models import Variable
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow import configuration as conf
from kubernetes.client import models as k8s
from airflow.settings import AIRFLOW_HOME
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
import pandas as pd
import os
from gcloud import storage
from docker.types import Mount
os.environ["GCLOUD_PROJECT"] = Variable.get("GCLOUD_PROJECT")
project_root = Variable.get("PROJECT_ROOT")
snowflake_user = Variable.get("SNOWFLAKE_USER")
snowflake_password = Variable.get("SNOWFLAKE_PASSWORD")
snowflake_account = Variable.get("SNOWFLAKE_ACCOUNT")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client.from_service_account_json(
        project_root + '/creds.json')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))
    
secret_dir = Mount(target='/secret',
                     source=project_root,
                     type='bind')

default_args = {
    'owner': 'dixon',
    'depends_on_past': False,
    'email': ['dixon2678@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
creds = Variable.get("google_creds", deserialize_json=False)
with DAG(
    'Data-Pipeline',
    default_args=default_args,
    description='EL pipeline from Binance API to Snowflake',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    tags=['dag'],
) as dag:
    # Echoing the environment variables (credentials, etc) to access.json file

    t1 = BashOperator(
        task_id='access_key',
        bash_command='echo {{ var.value.google_creds }} > ' + project_root + '/creds.json',
    )
    

    t2 = DockerOperator(
        task_id='pull_data',
        image='ghcr.io/dixon2678/el-snowflake:main',
        api_version='auto',
        auto_remove=True,
        mounts=[secret_dir],
        environment={
        'PROJECT_ROOT': project_root,
        'GCLOUD_PROJECT': os.environ["GCLOUD_PROJECT"]
        }
    )

    t3 = PythonOperator(
        task_id='download_tmpcsv',
        python_callable= download_blob,
        op_kwargs = {"bucket_name" : "binance_project", "source_blob_name" : "tmpcsv.csv", "destination_file_name" : project_root + "/tmpcsv.csv"},
        dag=dag,
    )

    t4 = BashOperator(
        task_id='ge_checkpoint',
        bash_command='cd '+ project_root + ' && great_expectations --v3-api checkpoint run data_pull || true'
    )
    
    t5 = DockerOperator(
        task_id='push_data',
        image='ghcr.io/dixon2678/el-snowflake:main',
        api_version='auto',
        auto_remove=True,
        mounts=[secret_dir],
        entrypoint='python3 /connectors/snowflake_conn.py',
        environment={
        'PROJECT_ROOT': project_root,
        'GCLOUD_PROJECT': os.environ["GCLOUD_PROJECT"],
        'SNOWFLAKE_USER': snowflake_user,
        'SNOWFLAKE_PASSWORD': snowflake_password,
        'SNOWFLAKE_ACCOUNT': snowflake_account
        }
    )
    
    
    t1 >> t2 >> t3 >> t4 >> t5
