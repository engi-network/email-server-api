import json

import requests

URL = "http://127.0.0.1:5000"
EMAIL = "christopherkelly@engi.network"
CONTACT_LIST_NAME = "engi-newsletter"
TOPICS = [CONTACT_LIST_NAME]
DATA = {"email": EMAIL, "contact_list_name": CONTACT_LIST_NAME}
ATTRS = json.dumps({"name": "chris", "favoriteanimal": "bonobo"})


class TestContact:
    endpoint = f"{URL}/contact"

    def test_should_be_able_to_add_contact(self):
        assert (
            requests.post(
                TestContact.endpoint,
                data={
                    **DATA,
                    "topics": TOPICS,
                    "attributes": ATTRS,
                },
            ).status_code
            == 200
        )

    def test_should_be_able_to_check_contact(self):
        r = requests.get(TestContact.endpoint, params=DATA)
        assert r.status_code == 200
        meta = r.json()
        assert meta["ContactListName"] == CONTACT_LIST_NAME
        assert meta["EmailAddress"] == EMAIL
        assert [d["TopicName"] for d in meta["TopicPreferences"]] == TOPICS
        assert meta["AttributesData"] == ATTRS

    def test_should_be_able_to_delete_contact(self):
        assert requests.delete(TestContact.endpoint, data=DATA).status_code == 200


def test_should_be_able_to_ping_server():
    assert requests.get(f"{URL}/ping").json() == "pong"
