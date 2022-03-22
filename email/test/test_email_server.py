import json
import os
import time

import pytest
import requests

URL = "http://127.0.0.1:8000"
EMAIL = os.environ["EMAIL"]
FROM_EMAIL = os.environ.get("FROM_EMAIL", EMAIL)
CONTACT_LIST_NAME = "engi-newsletter"
TEMPLATE_NAME = "engi-newsletter-welcome-template"
TOPICS = [CONTACT_LIST_NAME, "engi-programmer", "engi-business", "engi-investor", "engi-curious"]
DATA = {"email": EMAIL, "contact_list_name": CONTACT_LIST_NAME}
DEFAULT_ATTRS = json.dumps({"name": "friend", "favoriteanimal": "elephant"})
ATTRS = json.dumps({"name": "chris", "favoriteanimal": "bonobo"})


def test_should_be_able_to_ping_server():
    assert requests.get(f"{URL}/ping").json() == "pong"


class TestContact:
    endpoint = f"{URL}/contact"

    @pytest.mark.dependency()
    def test_should_be_able_to_create_contact(self):
        assert (
            requests.post(
                TestContact.endpoint,
                data={
                    **DATA,
                    "send_welcome_email": False,
                },
            ).status_code
            == 200
        )

    @pytest.mark.dependency(depends=["TestContact::test_should_be_able_to_create_contact"])
    def test_should_be_able_to_read_contact(self):
        r = requests.get(TestContact.endpoint, params=DATA)
        assert r.status_code == 200
        meta = r.json()
        assert meta["ContactListName"] == CONTACT_LIST_NAME
        assert meta["EmailAddress"] == EMAIL

    @pytest.mark.dependency(depends=["TestContact::test_should_be_able_to_create_contact"])
    def test_should_be_able_to_update_contact_subscribe(self):
        # subscribe to topics and update attributes
        r = requests.put(
            TestContact.endpoint,
            data={**DATA, "topics": TOPICS, "attributes": ATTRS},
        )
        assert r.status_code == 200
        # get the contact again
        r = requests.get(TestContact.endpoint, params=DATA)
        meta = r.json()
        assert set([d["TopicName"] for d in meta["TopicPreferences"]]) == set(TOPICS)
        assert meta["AttributesData"] == ATTRS

    @pytest.mark.dependency(depends=["TestContact::test_should_be_able_to_create_contact"])
    def test_should_be_able_to_update_contact_unsubscribe(self):
        topic = TOPICS[-1]
        # unsubscribe from topic
        r = requests.put(
            TestContact.endpoint,
            data={**DATA, "topics_unsubscribe": [topic]},
        )
        assert r.status_code == 200
        # get the contact again
        r = requests.get(TestContact.endpoint, params=DATA)
        meta = r.json()
        # make sure we are indeed now unsubscribed
        assert (
            dict([(d["TopicName"], d["SubscriptionStatus"]) for d in meta["TopicPreferences"]])[
                topic
            ]
            == "OPT_OUT"
        )

    @pytest.mark.skip(reason="don't send bulk messages once customers are on the list")
    @pytest.mark.dependency(depends=["TestContact::test_should_be_able_to_create_contact"])
    def test_should_be_able_to_send_msg(self):
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
        assert r.status_code == 202
        # fudge enough time for the backend to send a test message before the
        # fixture is torn down and the contact we're sending to is deleted
        time.sleep(2)

    @pytest.mark.dependency(
        depends=["TestContact::test_should_be_able_to_update_contact_unsubscribe"]
    )
    def test_should_be_able_to_delete_contact(self):
        assert requests.delete(TestContact.endpoint, data=DATA).status_code == 200

    @pytest.mark.dependency()
    def test_should_be_able_to_create_contact_with_welcome_message(self):
        assert (
            requests.post(
                TestContact.endpoint,
                data={
                    **DATA,
                    "send_welcome_email": True,
                    "attributes": ATTRS,
                },
            ).status_code
            == 200
        )
        # fudge enough time for the backend to send a test message before the
        # fixture is torn down and the contact we're sending to is deleted
        time.sleep(2)

    @pytest.mark.dependency(
        depends=["TestContact::test_should_be_able_to_create_contact_with_welcome_message"]
    )
    def test_should_be_able_to_delete_contact2(self):
        assert requests.delete(TestContact.endpoint, data=DATA).status_code == 200
