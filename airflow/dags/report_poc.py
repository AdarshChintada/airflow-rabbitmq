from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pymongo
import requests
import smtplib
import os
import json
from airflow.utils.dates import days_ago
from airflow.utils.email import send_email

# MongoDB Configuration
MONGO_DB_NAME = "airflowdb"
MONGO_COLLECTION_NAME = "client_schedules"
MONGO_URL = "mongodb://scheduledb:27017"

# Report Generator API placeholder
REPORT_GENERATOR_API_URL =  "https://537f-103-140-18-66.ngrok-free.app/generate_dailysale/"  # Replace with actual URL
EXCEL_WORKBOOK_PATH = "/opt/airflow/dags/Flash_Report_12-01-2024.xlsx"  # Replace with actual path

# Email SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "saichintada2@gmail.com"
SMTP_PASSWORD = "etlbqinniirotnwq"
FROM_EMAIL = "saichintada2@gmail.com"

# Failure Callback Email Function
def task_failure_email(context):
    # Get the task instance and task details
    task_instance = context.get("task_instance")
    task_id = task_instance.task_id
    dag_id = task_instance.dag_id
    exception = context.get('exception')

    # Create the email subject and message
    subject = f"Airflow Task Failed: {dag_id} - {task_id}"
    message = f"Task {task_id} of DAG {dag_id} failed. Error: {exception}\n\n"

    # Optionally add logs from the task instance
    log_url = task_instance.log_url
    message += f"Logs can be found at: {log_url}"

    # Send the email
    send_email(
        to=FROM_EMAIL,  # or a list of recipients
        subject=subject,
        html_content=message,
    )

# Task 1: Fetch client schedules from MongoDB
def fetch_schedule_from_db(**kwargs):
    client = pymongo.MongoClient(MONGO_URL)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    schedules = list(collection.find({}, {"_id": 0}))
    print(schedules)
    client.close()
    kwargs['ti'].xcom_push(key="client_data", value=schedules)

# Task 2: Call Report Generator API to generate reports
def generate_reports(**kwargs):
    client_data = kwargs['ti'].xcom_pull(key="client_data", task_ids="fetch_schedule")
    reports = {}

    for client in client_data:
        client_name = client['email']
        with open(EXCEL_WORKBOOK_PATH, "rb") as excel_file:
            files = {"file": excel_file}
            data = {"date": "12-01-2024"}
            response = requests.post(REPORT_GENERATOR_API_URL, files=files, data=data)
            reports[client_name] = response.json()

    # Save reports to a file for debugging
    with open("/tmp/daily_reports.json", "w") as file:
        json.dump(reports, file)

    kwargs['ti'].xcom_push(key="reports", value=reports)

    return reports

# Task 3: Send the reports to clients via email
def send_reports_via_email(**kwargs):
    client_data = kwargs['ti'].xcom_pull(key="client_data", task_ids="fetch_schedule")
    print("client data is:", client_data)
    reports = kwargs['ti'].xcom_pull(key="reports", task_ids="generate_reports")
    print("reports are:", reports)
    
    for client in client_data:
        client_name = client['email']
        delivery_pref = client['services']
        report = reports.get(client_name)
        
        if "email" in delivery_pref:
            recipient_email = client['email']
            subject = f"Daily Sales Report for {client_name}"
            message = f"Hello {client_name},\n\nPlease find your daily sales report attached.\n\nBest Regards."

            # Send email using SMTP
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                email_message = f"Subject: {subject}\n\n{message}"
                server.sendmail(FROM_EMAIL, recipient_email, email_message)

            print(f"Email sent to {recipient_email}")
        
        elif delivery_pref == "whatsapp":
            print(f"WhatsApp message sent to {client_name}")
        elif delivery_pref == "sms":
            print(f"SMS sent to {client_name}")
        elif delivery_pref == "imessage":
            print(f"iMessage sent to {client_name}")

# Define the DAG
with DAG(
    dag_id="Report_POC",
    schedule_interval="0 15 * * *",  # Runs daily at 3:00 PM
    start_date=datetime(2023, 1, 1),
    default_args={
        "retries": 1,
        "retry_delay": timedelta(seconds=2),
        "email_on_failure": True,
        "email": ["saichintada2@gmail.com"],  # Add your recipient email here
        "retry_on_failure": True,
        "on_failure_callback": task_failure_email,  # Attach the failure callback
    },
    catchup=False,
) as dag:

    fetch_schedule = PythonOperator(
        task_id="fetch_schedule",
        python_callable=fetch_schedule_from_db,
        op_kwargs={},
    )

    generate_reports_task = PythonOperator(
        task_id="generate_reports",
        python_callable=generate_reports,
        op_kwargs={},
    )

    send_reports_task = PythonOperator(
        task_id="send_reports",
        python_callable=send_reports_via_email,
        provide_context=True,
    )

    fetch_schedule >> generate_reports_task >> send_reports_task



# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime, timedelta
# import pymongo
# import requests
# import smtplib
# import os
# import json

# # MongoDB Configuration
# MONGO_DB_NAME = "airflowdb"
# MONGO_COLLECTION_NAME = "client_schedules"
# MONGO_URL = "mongodb://scheduledb:27017"


# # Report Generator API placeholder
# REPORT_GENERATOR_API_URL = "https://537f-103-140-18-66.ngrok-free.app/generate_dailysale/"  # Replace with actual URL
# EXCEL_WORKBOOK_PATH = "/opt/airflow/dags/Flash_Report_12-01-2024.xlsx"  # Replace with actual path

# # Email SMTP Configuration
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "saichintada2@gmail.com"
# SMTP_PASSWORD = "etlbqinniirotnwq"
# FROM_EMAIL = "saichintada2@gmail.com"

# #task 1: Fetch client schedules from MongoDB. 
# def fetch_schedule_from_db(**kwargs):
#     client = pymongo.MongoClient(MONGO_URL)
#     db = client[MONGO_DB_NAME]
#     collection = db[MONGO_COLLECTION_NAME]
#     schedules = list(collection.find({}, {"_id": 0}))
#     print(schedules)
#     client.close()
#     kwargs['ti'].xcom_push(key="client_data", value=schedules)

# # task 2: Call Report Generator API to generate reports.
# def generate_reports(**kwargs):
#     client_data = kwargs['ti'].xcom_pull(key="client_data", task_ids="fetch_schedule")
#     reports = {}
    
#     for client in client_data:
#         client_name = client['email']
#         with open(EXCEL_WORKBOOK_PATH, "rb") as excel_file:
#             files = {"file": excel_file}
#             data = {"date": "12-01-2024"}
#             response = requests.post(REPORT_GENERATOR_API_URL, files=files, data=data)
#             reports[client_name] = response.json()
        
#     # Save reports to a file for debugging
#     with open("/tmp/daily_reports.json", "w") as file:
#         json.dump(reports, file)

#     kwargs['ti'].xcom_push(key="reports", value=reports)
    
#     return reports

# # task 3: Send the reports to clients via email.
# def send_reports_via_email(**kwargs):
#     client_data = kwargs['ti'].xcom_pull(key="client_data", task_ids="fetch_schedule")
#     print("client data is:", client_data)
#     reports = kwargs['ti'].xcom_pull(key="reports", task_ids="generate_reports")
#     print("reports are:", reports)
#     for client in client_data:
#         client_name = client['email']
#         delivery_pref = client['services']
#         report = reports.get(client_name)
#         if "email" in delivery_pref:
#             recipient_email = client['email']
#             subject = f"Daily Sales Report for {client_name}"
#             message = f"Hello {client_name},\n\nPlease find your daily sales report attached.\n\nBest Regards."
            
#             # Send email using SMTP
#             with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#                 server.starttls()
#                 server.login(SMTP_USERNAME, SMTP_PASSWORD)
#                 email_message = f"Subject: {subject}\n\n{message}"
#                 server.sendmail(FROM_EMAIL, recipient_email, email_message)
            
#             print(f"Email sent to {recipient_email}")
#         elif delivery_pref == "whatsapp":
#             print(f"WhatsApp message sent to {client_name}")
#         elif delivery_pref == "sms":
#             print(f"SMS sent to {client_name}")
#         elif delivery_pref == "imessage":
#             print(f"iMessage sent to {client_name}")

# # Define the DAG
# with DAG(
#     dag_id="Report_POC",
#     schedule_interval="0 15 * * *",  # Runs daily at 3:00 PM
#     start_date=datetime(2023, 1, 1),
#     default_args={"retries": 1, "retry_delay": timedelta(seconds=2)},
#     catchup=False,
# ) as dag:
    
#     fetch_schedule = PythonOperator(
#         task_id="fetch_schedule",
#         python_callable=fetch_schedule_from_db,
#         op_kwargs={}
#     )
    
#     generate_reports_task = PythonOperator(
#         task_id="generate_reports",
#         python_callable=generate_reports,
#          op_kwargs={}
#     )
    
#     send_reports_task = PythonOperator(
#         task_id="send_reports",
#         python_callable=send_reports_via_email,
#         provide_context=True
#     )

#     fetch_schedule >>  send_reports_task
