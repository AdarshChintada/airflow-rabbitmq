from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from datetime import datetime, timedelta


# Define or Instantiate DAG
dag = DAG(
    'Email_POC',
    start_date=datetime(2025, 1, 24),
    schedule_interval='34 16 * * *', # Run daily at 15:36 (3:36 PM)
    catchup=False
)

welcome_task = BashOperator(
    task_id='welcome',
    bash_command='echo "Welcome to the ETL pipeline!"',
    dag=dag,
)



send_email_task = EmailOperator(
    task_id='send_email',
    to='adarshchintada2@gmail.com',
    subject='Daily sale report generated',
    html_content='Hi, the daily sale report has been generated.',
    dag=dag,
)

# Define Task Dependencies
welcome_task >> send_email_task