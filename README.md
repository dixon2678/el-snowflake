# el-snowflake

An EL (Extract-Load) script to Snowflake Cloud Data Warehouse.

## Architecture Diagram

<img width="970" alt="Screen Shot 2021-12-05 at 10 00 22 PM" src="https://user-images.githubusercontent.com/81808129/144749622-c25ca41d-a5ec-4cff-aacd-631a6c7dfa14.png">

## Tools/Frameworks Used

- Docker : Deploying a script with a lot of dependencies is often a troublesome process. Docker solves this problem by packaging the script, libraries, and runtime in a single container. The container then can be ran anywhere on all machines (local or cloud) and all Operating Systems, given it can run Docker Container Engine. Docker is the foundation of this project, allowing this pipeline to be deployed anywhere (e.g. migration to cloud!) with minimal trouble.

- Airflow : A workflow orchestrator, simplifying the management of complex workflows. Airflow workflows are written in DAGs (Directed Acyclic Graph) with Python (Configurations-as-Code). Airflow is commonly used in modern data pipelines

- PySpark : Python API for Spark. Spark is a data processing framework that is designed for Big Data Analytics, leveraging Parallel Processing and is written in Scala

- Great Expectations : A new and promising Python library, designed for data quality testing and validation. Great Expectations comes with intuitive configurators and HTML based Data Docs. Great Expectations can be easily integrated to data pipelines, and Airflow has an operator for Great Expectations tasks (GreatExpectationsOperator).


## Services Used

- Binance API: Binance REST API is used to gather a dataset of Cryptocurrency prices

- Google Cloud Storage (Data Lake): Storage Bucket for staging area

- Snowflake: Main Analytical Cloud Data Warehouse used for this Project

## Airflow DAG Graph

<img width="1361" alt="Screen Shot 2021-12-05 at 10 18 03 PM" src="https://user-images.githubusercontent.com/81808129/144750342-1a98512e-d774-4e3f-b1d5-3ff929c9d16c.png">

- access_key - BashOperator: Bash command to store the google_creds environment variable to the project path
- pull_data - DockerOperator: Pull Docker image from GitHub's Packages Container Registry - Python Script to pull data from Binance API, preprocess with Spark, and Upload to GCS Bucket. (WIP: Add testing to Raw Binance data with Great Expectations)
- download_tmpcsv - PythonOperator: Download csv temporary data from GCS Bucket.
- ge_checkpoint - BashOperator: Run a Great Expectations checkpoint to validate the temporary csv data. Currently this task is set to succeed no matter what is the outcome of the tests (WIP: Tune the expectation suite to better suit the requirements).
- push_data - DockerOperator: If the previous tasks succeed, upload the temporary csv data as final data to Snowflake.
