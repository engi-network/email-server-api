import os

from celery import Celery
from celery.utils.log import get_task_logger
from kombu.utils.url import safequote

from bulk_email import send_bulk_email
from send_contact_us_email import send_contact_us_email
from send_welcome_email import send_welcome_email

aws_access_key = safequote(os.environ["AWS_ACCESS_KEY_ID"])
aws_secret_key = safequote(os.environ["AWS_SECRET_ACCESS_KEY"])
queue_name_prefix = safequote(os.environ.get("QUEUE_NAME_PREFIX", "dev"))

log = get_task_logger(__name__)


app = Celery(
    "tasks",
    broker=f"sqs://{aws_access_key}:{aws_secret_key}@",
    broker_transport_options={"queue_name_prefix": f"{queue_name_prefix}-email-server-"},
)

print(f"{queue_name_prefix=}")


@app.task
def add(x, y):
    return x + y


@app.task
def async_send_bulk_email(*args):
    log.info(f"{args=}")
    return send_bulk_email(*args)


@app.task
def async_send_welcome_email(*args):
    log.info(f"{args=}")
    return send_welcome_email(*args)


@app.task
def async_send_contact_us_email(*args):
    log.info(f"{args=}")
    return send_contact_us_email(*args)
