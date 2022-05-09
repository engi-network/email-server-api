import os

if __name__ == "__main__":
    for key in [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_DEFAULT_REGION",
        "PYTHONPATH",
        "QUEUE_NAME_PREFIX",
        "EMAIL",
        "FROM_EMAIL",
    ]:
        val = os.environ[key]
        print(f"{key}={val}")
