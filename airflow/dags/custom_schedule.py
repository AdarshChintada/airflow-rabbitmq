# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime, timedelta
# import pytz
# import smtplib
# # Email SMTP Configuration
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "saichintada2@gmail.com"
# SMTP_PASSWORD = "etlbqinniirotnwq"
# FROM_EMAIL = "saichintada2@gmail.com"


# def fetch_client_schedules():
#     # Fetch the schedules for each client from the database
#     return [
#         {'client_id': 1, 'schedule_time': '12:30', 'email': 'adarshchintada2@gmail.com', 'frequency': 'daily'},
#         {'client_id': 2, 'schedule_time': '12:25', 'email': 'adarsh.chintada@nimbleaccounting.com', 'frequency': 'daily'},
#         {'client_id': 3, 'schedule_time': '12:32', 'email': 'adarsh.chintada@nimbleaccounting.com', 'frequency': 'daily'}
#     ]

# def send_report(client_email, schedule_time):
#     recipient_email = client_email
#     subject = f"Daily Sales Report for {client_email}"
#     message = f"Hello {recipient_email},\n\nPlease find your daily sales report attached.\n\nBest Regards."
    
#     # Send email using SMTP
#     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#         server.starttls()
#         server.login(SMTP_USERNAME, SMTP_PASSWORD)
#         email_message = f"Subject: {subject}\n\n{message}"
#         server.sendmail(FROM_EMAIL, recipient_email, email_message)
    
#     pass

# def create_dynamic_tasks():
#     schedules = fetch_client_schedules()
#     tasks = []
#     for schedule in schedules:
#         client_id = schedule['client_id']
#         client_email = schedule['email']
#         schedule_time = schedule['schedule_time']
        
#         # Calculate the next execution time based on the schedule_time
#         task = PythonOperator(
#             task_id=f"send_report_client_{client_id}",
#             python_callable=send_report,
#             op_args=[client_email, schedule_time],
#             dag=dag,
#             start_date=schedule_time,  # Adjust start_date based on schedule
#         )
#         tasks.append(task)
#     return tasks

# # DAG definition
# dag = DAG(
#     'daily_sale_reports',
#     schedule_interval=None,  # Don't run automatically, we'll trigger tasks dynamically
#     catchup=False,
#     start_date=datetime(2025, 1, 26),
# )

# # Dynamically create tasks
# create_dynamic_tasks()
