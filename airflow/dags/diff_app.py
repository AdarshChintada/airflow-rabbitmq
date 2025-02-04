# from airflow import DAG
# from airflow.operators.python import PythonOperator, BranchPythonOperator
# from datetime import datetime, timedelta
# import pytz

# def fetch_client_schedules():
#     # Simulating fetching client schedules from DB
#     return [
#         {'client_id': 1, 'schedule_time': '08:00', 'frequency': 'daily'},
#         {'client_id': 2, 'schedule_time': '15:00', 'frequency': 'daily'}
#     ]

# def send_report(client_id, schedule_time):
#     # Logic to send email
#     print(f"Sending report for client {client_id} at {schedule_time}")

# def check_schedule(client_id, schedule_time):
#     # Get the current UTC time
#     current_time = datetime.now(pytz.UTC)
    
#     # Parse the schedule_time (e.g., '08:00' -> 08:00)
#     schedule_hour, schedule_minute = map(int, schedule_time.split(":"))
    
#     # Calculate today's scheduled time for the client
#     schedule_time_today = current_time.replace(hour=schedule_hour, minute=schedule_minute, second=0, microsecond=0)
    
#     # If the scheduled time today has passed, check for tomorrow
#     if schedule_time_today < current_time:
#         schedule_time_today += timedelta(days=1)
    
#     # Return the result based on current time
#     if current_time >= schedule_time_today:
#         return f"send_report_{client_id}"  # Proceed with sending the report
#     else:
#         return f"skip_task_{client_id}"  # Skip the task if not time yet

# def skip_task():
#     print("It's not time to send the report yet.")

# # Define the DAG with an interval (e.g., every minute)
# dag = DAG(
#     'different_approach',
#     schedule_interval='* * * * *',  # Runs every minute to check schedules
#     catchup=False,
#     start_date=datetime(2025, 1, 27),
# )

# # Define the dynamic tasks for each client
# schedules = fetch_client_schedules()
# for schedule in schedules:
#     client_id = schedule['client_id']
#     schedule_time = schedule['schedule_time']
    
#     # Task to check the schedule and decide whether to run
#     check_schedule_task = BranchPythonOperator(
#         task_id=f"check_schedule_{client_id}",
#         python_callable=check_schedule,
#         op_args=[client_id, schedule_time],
#         provide_context=True,
#         dag=dag,
#     )

#     # Task to send the report if it's time
#     send_report_task = PythonOperator(
#         task_id=f"send_report_{client_id}",
#         python_callable=send_report,
#         op_args=[client_id, schedule_time],
#         dag=dag,
#     )

#     # Task to skip if it's not time
#     skip_task = PythonOperator(
#         task_id=f"skip_task_{client_id}",  # Unique task_id for each client
#         python_callable=skip_task,
#         dag=dag,
#     )

#     # Branching based on whether it's time to send the report
#     check_schedule_task >> [send_report_task, skip_task]
