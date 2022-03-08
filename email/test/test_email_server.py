import requests

URL = "http://127.0.0.1:5000"
EMAIL = "christopherkelly@engi.network"
TOPIC = "engi-newsletter"


def test_should_be_able_to_ping_server():
    endpoint = "ping"
    assert requests.get(f"{URL}/{endpoint}").json() == "pong"


def test_should_be_able_to_add_contact():
    endpoint = "contact"
    assert (
        requests.post(f"{URL}/{endpoint}", data={"email": EMAIL, "topic": TOPIC}).status_code
        == 200
    )


def test_should_be_able_to_check_contact():
    endpoint = "contact"
    assert requests.get(f"{URL}/{endpoint}", data={"email": EMAIL}).status_code == 200
