import json

import requests

URL = "http://127.0.0.1:5000"
EMAIL = "christopherkelly@engi.network"
FROM_EMAIL = "g@engi.network"
CONTACT_LIST_NAME = "engi-newsletter"
TEMPLATE_NAME = "engi-newsletter-welcome-template"
TOPICS = [CONTACT_LIST_NAME]
DATA = {"email": EMAIL, "contact_list_name": CONTACT_LIST_NAME}
DEFAULT_ATTRS = json.dumps({"name": "friend", "favoriteanimal": "elephant"})
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


def test_should_be_able_to_send_msg():
    r = requests.post(
        f"{URL}/send",
        data={
            "contact_list_name": CONTACT_LIST_NAME,
            "topic": CONTACT_LIST_NAME,
            "template_name": TEMPLATE_NAME,
            "from_email": FROM_EMAIL,
            "default_attributes": DEFAULT_ATTRS,
        },
    )
    assert r.status_code == 200
    assert all([k["Status"] == "SUCCESS" for k in r.json()["BulkEmailEntryResults"]])


def test_should_be_able_to_ping_server():
    assert requests.get(f"{URL}/ping").json() == "pong"
