import os

from celery import Celery
from kombu.utils.url import safequote

from bulk_email import send_bulk_email

aws_access_key = safequote(os.environ["AWS_ACCESS_KEY_ID"])
aws_secret_key = safequote(os.environ["AWS_SECRET_ACCESS_KEY"])


app = Celery("tasks", broker=f"sqs://{aws_access_key}:{aws_secret_key}@")


@app.task
def add(x, y):
    return x + y


@app.task
def async_send_bulk_email(*args):
    return send_bulk_email(*args)
