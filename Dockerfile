FROM python:3.11.2-slim-bullseye

ADD requirements.txt .

RUN pip install -r requirements.txt