### A backend server for the engi-network website

`email` contains a server to implement a simple REST API for email capture

### Install library dependencies from Pipfile

`pipenv install`

### Environment

You'll need the AWS credentials, see below

Create a `.env` file:
```
FLASK_DEBUG=1
FLASK_APP=api.py

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

`PYTHONPATH=email celery -A tasks worker --loglevel=INFO`

### Run the tests

`pipenv run pytest -v`