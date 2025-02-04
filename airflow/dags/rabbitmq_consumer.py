import pika
import json
import requests
import os

# RabbitMQ Configuration
RABBITMQ_HOST = "localhost"
QUEUE_NAME_REQUEST = "report_requests"
QUEUE_NAME_RESPONSE = "report_responses"

# Credentials
RABBITMQ_USER = "guest"
RABBITMQ_PASSWORD = "guest"

# Report Generator API URL
REPORT_GENERATOR_API_URL = "https://b8bc-103-140-18-66.ngrok-free.app/generate_dailysale/"

# Directory to store reports
REPORTS_DIR = "/opt/airflow/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def process_report_request(ch, method, properties, body):
    client_data = json.loads(body)
    email = client_data['email']
    
    # Ensure full path of Excel file
    excel_file = client_data.get('excel_file', '/opt/airflow/dags/Flash_Report_12-01-2024.xlsx')
    date = client_data.get('date', '12-01-2024')

    print(f"Processing report for {email} with Excel File: {excel_file}")

    # Prepare request payload
    with open(excel_file, "rb") as file:
        files = {"file": file}
        data = {"date": date}
        
        # Send request to the API
        response = requests.post(REPORT_GENERATOR_API_URL, files=files, data=data)
    
    if response.status_code == 200:
        report_data = response.json()  # Assuming API returns JSON report data
    else:
        report_data = {"status": "failed", "error": response.text}

    # Store response as JSON (simulating a report PDF)
    report_file_path = f"/opt/airflow/reports/{email.replace('@', '_')}.json"
    with open(report_file_path, "w") as f:
        json.dump(report_data, f)

    # Push report into RabbitMQ Response Queue
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=5672, credentials=credentials))
        channel = connection.channel()
        
        channel.queue_declare(queue=QUEUE_NAME_RESPONSE, durable=True)

        report_message = json.dumps({"email": email, "report_file": report_file_path})
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME_RESPONSE,
            body=report_message,
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )

        print(f"Report for {email} saved and pushed to response queue.")

    except pika.exceptions.AMQPConnectionError as e:
        print(f"RabbitMQ Connection failed: {e}")
    
    finally:
        if 'connection' in locals():
            connection.close()

# RabbitMQ Consumer Setup
try:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=5672, credentials=credentials))
    channel = connection.channel()
    
    channel.queue_declare(queue=QUEUE_NAME_REQUEST, durable=True)

    # Start consuming messages
    channel.basic_consume(queue=QUEUE_NAME_REQUEST, on_message_callback=process_report_request, auto_ack=True)
    print("Waiting for report requests...")

    channel.start_consuming()

except pika.exceptions.AMQPConnectionError as e:
    print(f"RabbitMQ Connection Error: {e}")

