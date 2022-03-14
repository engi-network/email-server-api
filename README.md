## A backend server for the engi-network website

### Email Capture Server

A server to implement a simple REST API for email capture and integration with
AWS SES and SQS for sending mass marketing emails

See the [ticket in Linear](https://linear.app/engi/issue/ENGIN-118/add-emailuser-typ)

The `email` directory contains a server to implement a simple REST API for email capture

### Install library dependencies from Pipfile

`pipenv install`

### Environment

You'll need the AWS credentials, see below

Create a `.env` file:
```
FLASK_DEBUG=1
FLASK_APP=api.py
PYTHONPATH=email
EMAIL="christopherkelly@engi.network"

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION="us-west-2"
```

### Start the email server and background worker

Run these locally or in Docker (not both)

#### Docker

`docker-compose up`

#### Locally

Start the REST API server:

`pipenv run flask run -h 0.0.0.0 -p 8000`

Run the background worker in a separate terminal:

`pipenv run celery -A tasks worker --loglevel=INFO`

### Run the tests

An email should be sent to the address in the `EMAIL` var in your `.env` file

`pipenv run pytest -v`