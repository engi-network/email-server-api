import requests

URL = "http://localhost:5000/"


def test_should_be_able_to_ping_server():
    endpoint = "ping"
    requests.get(f"{URL}/{endpoint}").json() == "pong"
