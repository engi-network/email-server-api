import requests

URL = "http://127.0.0.1:5000/"


def test_should_be_able_to_ping_server():
    endpoint = "ping"
    requests.get(f"{URL}/{endpoint}").json() == "pong"
