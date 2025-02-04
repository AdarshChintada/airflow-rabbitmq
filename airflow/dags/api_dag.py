import json
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.providers.http.sensors.http import HttpSensor  
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
import requests

def call_api_with_file_and_date():
    # Static date
    date = '12-01-2024'
    
    # File path (ensure this path is correct)
    file_path = '/opt/airflow/dags/Flash_Report_12-01-2024.xlsx'  # Replace with actual file path
    
    # API endpoint
    url = 'https://537f-103-140-18-66.ngrok-free.app/generate_dailysale/'  # Replace with actual API URL
    
    # Prepare the file and the data (static date)
    files = {'file': open(file_path, 'rb')}
    data = {'date': date}
    
    # Send the POST request with file and data
    response = requests.post(url, files=files, data=data)
    
    # Ensure to close the file after request
    files['file'].close()
    
    if response.status_code == 200:
        print("Request was successful!")
        return response.json()  # or response.text based on API response
    else:
        raise Exception(f"API request failed with status code {response.status_code}")



with DAG(
    dag_id = 'api_dag',
    schedule_interval = '0 0 * * *', # Run daily at 00:00 (12:00 AM)
    start_date = datetime(2025, 1, 24),
    catchup = False
) as dag:
    
    # #task1: To check API is active or not
    # api_active = HttpSensor(
    #     task_id = 'is_api_active',
    #     http_conn_id = 'dailysale_reportgen',
    #     endpoint = 'posts/'
    # )

    #task2: To fetch data from API
    # Replace task2 with a PythonOperator to call the function
    call_api_with_file = PythonOperator(
        task_id='call_api_with_file',
        python_callable=call_api_with_file_and_date,
        dag=dag,
    )

