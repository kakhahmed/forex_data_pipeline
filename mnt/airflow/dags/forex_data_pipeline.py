import csv
import json
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.hive_operator import HiveOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.slack.operators.slack_webhook import \
    SlackWebhookOperator
from airflow.sensors.filesystem import FileSensor

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 3,
    "retry_delay": timedelta(minutes=5)
}


def _get_message() -> str:
    return "Hi from Forex data pipeline!"

# Download forex rates according to the currencies we want to watch
# described in the file forex_currencies.csv
def download_rates():
    BASE_URL = "https://gist.githubusercontent.com/marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b/raw/"
    ENDPOINTS = {
        'USD': 'api_forex_exchange_usd.json',
        'EUR': 'api_forex_exchange_eur.json'
    }
    with open('/opt/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for idx, row in enumerate(reader):
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get(f"{BASE_URL}{ENDPOINTS[base]}").json()
            outdata = {'base': base, 'rates': {}, 'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/opt/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')


with DAG(
    "forex_data_pipeline",
    start_date=datetime(2021, 1, 1),
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
) as dag:

    forex_rates_available = HttpSensor(
        task_id="forex_rates_available",
        http_conn_id="forex_api",
        endpoint="marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b",
        response_check=lambda response: "rates" in response.text,
        poke_interval=5,  # in seconds
        timeout=20,
    )

    forex_currencies_files_available = FileSensor(
        task_id="forex_currencies_files_available",
        fs_conn_id="forex_path",
        filepath="forex_currencies.csv",
        poke_interval=5,  # in seconds
        timeout=20,
    )

    downloading_rates = PythonOperator(
        task_id="downloading_rates",
        python_callable=download_rates,
    )

    saving_rates = BashOperator(
        task_id="saving_rates",
        bash_command="""
            hdfs dfs -mkdir -p /forex && \
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
        """
    )

    # Use Hive interact with data stored in HDFS.
    create_table = HiveOperator(
        task_id="creating_forex_rates_table",
        hql="""
            CREATE EXTERNAL TABLE IF NOT EXISTS forex_rates(
                base STRING,
                last_update DATE,
                eur DOUBLE,
                usd DOUBLE,
                nzd DOUBLE,
                gbp DOUBLE,
                jpy DOUBLE,
                cad DOUBLE
                )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """,
        hive_cli_conn_id="hive_conn",
    )

    forex_processing = SparkSubmitOperator(
        task_id="forex_processing",
        conn_id="spark_conn",
        application="/opt/airflow/dags/scripts/forex_processing.py",
        verbose=True,
        
    )

    send_email_notification = EmailOperator(
        task_id="send_email_notification",
        to="airflow_course@yopmail.com",
        subject="forex_data_pipeline",
        html_content="<h3>forex_data_pipeline</h3>",
    )

    send_slack_notification = SlackWebhookOperator(
        task_id="send_slack_notification",
        http_conn_id="slack_conn",
        webhook_token="<Add_SLACK_WEBHOOK_TOKEN>",
        message=_get_message(),
        channel="#tests-for-airflow"
    )

    forex_rates_available >> forex_currencies_files_available
    forex_currencies_files_available >> downloading_rates >> saving_rates
    saving_rates >> create_table >> forex_processing
    forex_processing >> send_email_notification
    forex_processing >> send_slack_notification
