### A backend server for the engi-network website

`email` contains a server to implement a simple REST API for email capture

### Install library dependencies from Pipfile

`pipenv install`

### Start the email server and background worker

Run these locally or in Docker (not both).

#### Docker

`docker-compose up`

#### Locally

Start the REST API server:

`PYTHONPATH=email FLASK_APP=api.py pipenv run flask run -h 0.0.0.0 -p 8000`

Run the background worker in a separate terminal:

`PYTHONPATH=email celery -A tasks worker --loglevel=INFO`

### Run the tests

`pipenv run pytest -v`