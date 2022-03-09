import requests

URL = "http://127.0.0.1:5000"
EMAIL = "christopherkelly@engi.network"
TOPIC = "engi-newsletter"
DATA = {"email": EMAIL, "topic": TOPIC}


class TestContact:
    endpoint = f"{URL}/contact"

    def test_should_be_able_to_add_contact(self):
        assert requests.post(TestContact.endpoint, data=DATA).status_code == 200

    def test_should_be_able_to_check_contact(self):
        r = requests.get(TestContact.endpoint, params=DATA)
        assert r.status_code == 200
        meta = r.json()
        assert meta["ContactListName"] == TOPIC
        assert meta["EmailAddress"] == EMAIL

    def test_should_be_able_to_delete_contact(self):
        assert requests.delete(TestContact.endpoint, data=DATA).status_code == 200


def test_should_be_able_to_ping_server():
    assert requests.get(f"{URL}/ping").json() == "pong"
