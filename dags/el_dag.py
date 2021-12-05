from datetime import timedelta
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators.docker_operator import DockerOperator
from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow import configuration as conf
from kubernetes.client import models as k8s

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
        bash_command='echo {{var.json.google_creds}} > creds.json',
    ),
    
    t2 = BashOperator(
        task_id='pull_data',
        bash_command='python3 /Users/dix/Desktop/portfolio/el-snowflake/source/main.py'
    ),


    t3 = BashOperator(
        task_id='push_data',
        bash_command='python3 /Users/dix/Desktop/portfolio/el-snowflake/connectors/snowflake_conn.py'
    )
    t1 >> t2 >> t3
