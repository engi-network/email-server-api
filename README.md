## A backend server for the engi-network website

### Email Capture Server

A server to implement a simple REST API for email capture and integration with
AWS SES and SQS for sending mass marketing emails

See the [ticket in Linear](https://linear.app/engi/issue/ENGIN-118/add-emailuser-typ)

The `email` directory contains a server to implement a simple REST API for email capture

### Install library dependencies from Pipfile

#### If you're using a Mac

And intend to run the Celery background worker (see below) outside of Docker:

```
brew install openssl@1.1
export PATH="/opt/homebrew/opt/openssl@1.1/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@1.1/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@1.1/lib/pkgconfig"
export PYCURL_SSL_LIBRARY=openssl
```

`pipenv install`

### Environment

You'll need the AWS credentials, see below

Create a `.env` file:
```
FLASK_DEBUG=1
FLASK_APP=api.py
PYTHONPATH=email
EMAIL="christopherkelly@engi.network"
FROM_EMAIL=${EMAIL}
QUEUE_NAME_PREFIX=dev

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION="us-west-2"
```

`${FROM_EMAIL}` needs to be verified for sending in SES.

### Start the email server and background worker

Run these locally or in Docker (not both)

#### Docker

`docker-compose up`

#### Locally

Start the REST API server:

`pipenv run flask run -h 0.0.0.0 -p 8000`

Run the background worker in a separate terminal:

`pipenv run celery -A tasks worker --loglevel=INFO`

Note the Celery broker uses an SQS queue named using the environment variable
`${QUEUE_NAME_PREFIX}`. Be careful about having multiple instances of `celery`
pulling jobs from the same queue as they will race each other.

### Run the tests

An email should be sent to the address in the `EMAIL` var in your `.env` file

`pipenv run pytest -v`

### Deploy

Terraform sources in the directory `deploy`

Two input variables to supply on the command line, or you can put them in
`deploy/terraform.tfvars` (but obviously don't check this file into Git):

```
aws_access_key_id     = ""
aws_secret_access_key = ""
```

These are the AWS credentials for the Docker container (and not necessarily
those required to run `terraform`).