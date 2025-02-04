FROM apache/airflow:latest

USER airflow

# Install Python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

