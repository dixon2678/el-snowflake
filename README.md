# el-snowflake

An EL (Extract-Load) script to Snowflake Cloud Data Warehouse. The pipeline fetches data from Binance's cryptocurrency prices API, preprocesses with Spark, data quality testing/validation with Great Expecatations, and loads it to Snowflake as the core Analytical DB. Almost all of the tasks are containerized with Docker, and Airflow is used for workflow orchestration. This project reflects my Data Engineering biases to E(t)LT process.

E - Extract : Extract Raw Data from Source
t - Pre-loading Transformation : Data Transformation stage. Note the small (t), that is because the transformations in this stage are very minor (e.g. ensuring correct formats for the DB) without too much altering the 'raw' state of the data.
L - Load : The arguably still 'raw' data are loaded into Data Warehouse
T - Data Modeling & Transformation : This is where major Transformations will take place. Adjusting to the requirements of business stakeholders, Data Analysts will be primarily in charge of this process and create SQL Data Models.

P.S. This project is intentionally over-engineered (for the comparatively small Binance API data), with the purpose of emulating a real-life analytical scenario with larger batches of data!

## Architecture Diagram

<img width="970" alt="Screen Shot 2021-12-05 at 10 00 22 PM" src="https://user-images.githubusercontent.com/81808129/144749622-c25ca41d-a5ec-4cff-aacd-631a6c7dfa14.png">

## Tools/Frameworks Used

- Docker : Deploying a script with a lot of dependencies is often a troublesome process. Docker solves this problem by packaging the script, libraries, and runtime in a single container. The container then can be ran anywhere on all machines (local or cloud) and all Operating Systems, given it can run Docker Container Engine. Docker is the foundation of this project, allowing this pipeline to be deployed anywhere (e.g. migration to cloud!) with minimal trouble.

- Airflow : A workflow orchestrator and scheduler, simplifying the management of complex workflows. Airflow workflows are written in DAGs (Directed Acyclic Graph) with Python (Configurations-as-Code). Airflow is commonly used in modern data pipelines

- PySpark : Python API for Spark. Spark is a data processing framework that is designed for Big Data Analytics, leveraging Parallel Processing and is written in Scala

- Great Expectations : A new and promising Python library, designed for data quality testing and validation. Great Expectations comes with intuitive configurators and HTML based Data Docs. Great Expectations can be easily integrated to data pipelines, and Airflow has an operator for Great Expectations tasks (GreatExpectationsOperator).


## Services Used

- Binance API: Binance REST API is used to gather a dataset of Cryptocurrency prices

- Google Cloud Storage (Data Lake): Storage Bucket for staging area

- Snowflake: Main Analytical Cloud Data Warehouse used for this Project

## Environment Variables for Airflow

Note: To avoid security issues and added complexity, using IAM instead of manually supplying credentials is heavily recommended. (WIP: Modify the Project to use IAM instead of secrets).

- GCLOUD_PROJECT : Google Cloud project name
- PROJECT_ROOT : Absolute path of the project's local instance 
- google_creds : Google Service Account credentials json file
- SNOWFLAKE_USER : Snowflake Username
- SNOWFLAKE_PASSWORD : Snowflake Password
- SNOWFLAKE_ACCOUNT : Snowflake Account

## Airflow DAG Graph

<img width="1361" alt="Screen Shot 2021-12-05 at 10 18 03 PM" src="https://user-images.githubusercontent.com/81808129/144750342-1a98512e-d774-4e3f-b1d5-3ff929c9d16c.png">

- access_key - BashOperator: Bash command to store the google_creds environment variable to the project path
- pull_data - DockerOperator: Pull Docker image from GitHub's Packages Container Registry - Python Script to pull data from Binance API, preprocess with Spark, and Upload to GCS Bucket. (WIP: Add testing to Raw Binance data with Great Expectations)
- download_tmpcsv - PythonOperator: Download csv temporary data from GCS Bucket.
- ge_checkpoint - BashOperator: Run a Great Expectations checkpoint to validate the temporary csv data. Currently this task is set to succeed no matter what is the outcome of the tests (WIP: Tune the expectation suite to better suit the requirements).
- push_data - DockerOperator: If the previous tasks succeed, upload the temporary csv data as final data to Snowflake.

## CI&CD on GitHub

A CI/CD pipeline with GitHub Actions is set up for this project. Every commit will be build into a Docker container and pushed to GitHub's Package Registry. The Airflow DAG will try to fetch the latest image from GitHub's Package Registry and run it with DockerOperator.

Unit Testing, Linting, and other intermediary steps between Build and Push are future additions to be implemented (WIP)

## How to run the Project

1. <a href="https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html">Install Airflow</a>
2. Set up a new Airflow user and Initialize Airflow's backend DB with airflow db init, scheduler with airflow scheduler, and webserver with airflow webserver -D
3. Access Airflow's webserver (0.0.0.0:8080 is the default address)
4. Navigate to Admin -> Variables <img width="602" alt="Screen Shot 2021-12-05 at 11 11 07 PM" src="https://user-images.githubusercontent.com/81808129/144752294-e4ed9935-b66e-4638-8a29-3eece3b74938.png">
5. Set up the above required variables
6. Ensure the DAG file is accessible by Airflow
7. Unpause the DAG and press the start button
<img width="1373" alt="Screen Shot 2021-12-05 at 11 12 53 PM" src="https://user-images.githubusercontent.com/81808129/144752383-4965decc-e186-4e5d-bfdd-5c91b1f24b43.png">
8. Pipeline is Running!

## Future Improvements
- (In Progress) Set up a dbt project in Docker for Data Modeling & Transformation
