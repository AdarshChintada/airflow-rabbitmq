from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pymongo
import json
import pika  # RabbitMQ
import os

# MongoDB Configuration
MONGO_DB_NAME = "airflowdb"
MONGO_COLLECTION_NAME = "client_schedules"
MONGO_URL = "mongodb://scheduledb:27017"

# RabbitMQ Configuration
RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME_REQUEST = "report_requests"
QUEUE_NAME_RESPONSE = "report_responses"

# Task 1: Fetch client schedules from MongoDB and push them to RabbitMQ queue
def fetch_schedule_from_db(**kwargs):
    client = pymongo.MongoClient(MONGO_URL)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    schedules = list(collection.find({}, {"_id": 0}))
    client.close()

    # Push client data to RabbitMQ queue for API processing
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME_REQUEST, durable=True)

    for client in schedules:
        message = json.dumps(client)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME_REQUEST,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        print(f"Pushed to queue: {client['email']}")

    connection.close()

# Task 2: Fetch processed reports from RabbitMQ response queue
def fetch_reports_from_queue(**kwargs):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME_RESPONSE, durable=True)

    def callback(ch, method, properties, body):
        report = json.loads(body)
        print(f"Fetched report for {report['email']}")

        # Push reports to XCom for next task
        kwargs['ti'].xcom_push(key=report['email'], value=report)

    # Consume all messages and stop
    channel.basic_consume(queue=QUEUE_NAME_RESPONSE, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

    connection.close()

# Task 3: Send reports based on client preference (email, WhatsApp, SMS, iMessage)
def send_reports(**kwargs):
    ti = kwargs['ti']
    connection = pymongo.MongoClient(MONGO_URL)
    db = connection[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    # Fetch all clients
    schedules = list(collection.find({}, {"_id": 0}))
    for client in schedules:
        email = client['email']
        delivery_pref = client['services']

        # Fetch report from XCom
        report = ti.xcom_pull(task_ids='fetch_reports', key=email)
        if not report:
            continue  # Skip if no report

        # Send based on preference
        if "email" in delivery_pref:
            print(f"Sending Email to {email} with Report")
        if "whatsapp" in delivery_pref:
            print(f"Sending WhatsApp message to {email}")
        if "sms" in delivery_pref:
            print(f"Sending SMS to {email}")
        if "imessage" in delivery_pref:
            print(f"Sending iMessage to {email}")

# Define the DAG
with DAG(
    dag_id="rabbitmq_POC",
    schedule_interval="0 15 * * *",
    start_date=datetime(2023, 1, 1),
    default_args={"retries": 1, "retry_delay": timedelta(seconds=2)},
    catchup=False,
) as dag:

    fetch_schedule = PythonOperator(
        task_id="fetch_schedule",
        python_callable=fetch_schedule_from_db,
    )

    fetch_reports = PythonOperator(
        task_id="fetch_reports",
        python_callable=fetch_reports_from_queue,
    )

    send_reports_task = PythonOperator(
        task_id="send_reports",
        python_callable=send_reports,
    )

    fetch_schedule >> fetch_reports >> send_reports_task
