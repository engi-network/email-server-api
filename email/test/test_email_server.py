import requests

URL = "http://127.0.0.1:5000"
EMAIL = "christopherkelly@engi.network"
TOPIC = "engi-newsletter"


class TestContact:
    endpoint = "contact"

    def test_should_be_able_to_add_contact(self):
        assert (
            requests.post(
                f"{URL}/{TestContact.endpoint}", data={"email": EMAIL, "topic": TOPIC}
            ).status_code
            == 200
        )

    def test_should_be_able_to_check_contact(self):
        assert (
            requests.get(f"{URL}/{TestContact.endpoint}", data={"email": EMAIL}).status_code == 200
        )

    def test_should_be_able_to_delete_contact(self):
        assert (
            requests.delete(f"{URL}/{TestContact.endpoint}", data={"email": EMAIL}).status_code
            == 200
        )


def test_should_be_able_to_ping_server():
    endpoint = "ping"
    assert requests.get(f"{URL}/{endpoint}").json() == "pong"
