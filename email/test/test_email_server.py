import requests

URL = "http://127.0.0.1:5000"


def test_should_be_able_to_ping_server():
    endpoint = "ping"
    assert requests.get(f"{URL}/{endpoint}").json() == "pong"


def test_should_be_able_to_add_contact():
    endpoint = "contact"
    email = "christopherkelly@engi.network"
    topic = "engi-newsletter"
    assert (
        requests.post(f"{URL}/{endpoint}", data={"email": email, "topic": topic}).status_code
        == 200
    )
