# Dockerfile
FROM python:latest
WORKDIR /code
COPY requirements.txt /code/
COPY . .
RUN pip install -r requirements.txt