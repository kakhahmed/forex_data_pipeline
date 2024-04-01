# The Forex Data Pipeline

This is a data pipeline built using airflow as an practical exercise to deepen my hands-on experience with Airflow along with other data tools.

This data pipeline is build while attending the [Apache Airflow: The Hands-On Guide](https://www.udemy.com/course/the-ultimate-hands-on-course-to-master-apache-airflow/?couponCode=GENAISALE24) online course on Udemy by [Marc Lamberti](https://www.udemy.com/course/the-ultimate-hands-on-course-to-master-apache-airflow/#instructor-1)


# TODO: Add Flow Chart of the Forex Data Pipeline.

- Check availability of forex rates: file name??

# TODO Add architecture.


# Running airflow


This package contains docker images for all needed packages.


Using the 4 bash scripts `start.sh`, `stop.sh`, `restart.sh`, `reset.sh`, you can control and run needed commands to build, run, stop the docker containers.




## Forex data pipeline

<img src="docs/forex_data_pipeline_graph_view.png" alt="drawing"/>


### Setting airflow connections
There are 5 different connections to set for this pipline

- Forex API HTTP connection
<img src="docs/forex_api_connection.png" alt="drawing" width="500"/>

- Forex path FTP connection
<img src="docs/forex_path_connection.png" alt="drawing" width="500"/>

- Hive connection
<img src="docs/hive_conn_connection.png" alt="drawing" width="500"/>

- Spark connection
<img src="docs/spark_conn_connection.png" alt="drawing" width="500"/>

- SlackWebhook connection
<img src="docs/slack_conn_connection.png" alt="drawing" width="500"/>
