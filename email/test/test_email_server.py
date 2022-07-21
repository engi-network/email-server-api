import json
import os
import time

import pytest
import requests
from default_params import (
    CONTACT_LIST_NAME,
    EMAIL,
    FROM_EMAIL,
    TEMPLATE_NAME,
    TEST_TOPIC,
    TOPICS,
)

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = os.environ.get("PORT", 8000)
URL = f"http://{HOST}:{PORT}"
TOPICS.append(TEST_TOPIC)
DATA = {"email": EMAIL, "contact_list_name": CONTACT_LIST_NAME}
DEFAULT_ATTRS = json.dumps({"first_name": "friend"})
ATTRS = json.dumps({"first_name": "Christopher"})
CONTACT_US = {
    "first_name": "Christopher",
    "last_name": "Kelly",
    "email": EMAIL,
    "subject": "Python support",
    "message": "Will Engi support Python and pytest?",
}


def test_should_be_able_to_ping_server():
    assert requests.get(f"{URL}/ping").json() == "pong"


class TestContactUs:
    endpoint = f"{URL}/contact_us"

    def test_should_be_able_to_contact_us(self):
        assert requests.post(TestContactUs.endpoint, json=CONTACT_US).status_code == 202


class TestContact:
    endpoint = f"{URL}/contact"

    @pytest.mark.dependency()
    def test_should_be_able_to_create_contact(self):
        assert (
            requests.post(
                TestContact.endpoint,
                json={
                    **DATA,
                    "send_welcome_email": False,
                },
            ).status_code
            == 200
        )

    @pytest.mark.dependency(depends=["TestContact::test_should_be_able_to_create_contact"])
    def test_should_be_able_to_read_contact(self):
        r = requests.get(TestContact.endpoint, json=DATA)
        assert r.status_code == 200
        meta = r.json()
        assert meta["ContactListName"] == CONTACT_LIST_NAME
        assert meta["EmailAddress"] == EMAIL

    @pytest.mark.dependency(depends=["TestContact::test_should_be_able_to_create_contact"])
    def test_should_be_able_to_update_contact_subscribe(self):
        # subscribe to topics and update attributes
        r = requests.put(
            TestContact.endpoint,
            json={**DATA, "topics": TOPICS, "attributes": ATTRS},
        )
        assert r.status_code == 200
        # get the contact again
        r = requests.get(TestContact.endpoint, json=DATA)
        meta = r.json()
        assert set([d["TopicName"] for d in meta["TopicPreferences"]]) == set(TOPICS)
        assert meta["AttributesData"] == ATTRS

    @pytest.mark.dependency(depends=["TestContact::test_should_be_able_to_create_contact"])
    def test_should_be_able_to_update_contact_unsubscribe(self):
        topic = TOPICS[0]
        # unsubscribe from topic
        r = requests.put(
            TestContact.endpoint,
            json={**DATA, "topics_unsubscribe": [topic]},
        )
        assert r.status_code == 200
        # get the contact again
        r = requests.get(TestContact.endpoint, json=DATA)
        meta = r.json()
        # make sure we are indeed now unsubscribed
        assert (
            dict([(d["TopicName"], d["SubscriptionStatus"]) for d in meta["TopicPreferences"]])[
                topic
            ]
            == "OPT_OUT"
        )

    @pytest.mark.dependency(depends=["TestContact::test_should_be_able_to_create_contact"])
    def test_should_be_able_to_send_msg(self):
        # careful! setting topic to anything other than the test topic will send
        # test messages to customers
        r = requests.post(
            f"{URL}/send",
            json={
                "contact_list_name": CONTACT_LIST_NAME,
                "topic": TEST_TOPIC,
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
        assert requests.delete(TestContact.endpoint, json=DATA).status_code == 200

    @pytest.mark.dependency()
    def test_should_be_able_to_create_contact_with_welcome_message(self):
        assert (
            requests.post(
                TestContact.endpoint,
                json={
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
        assert requests.delete(TestContact.endpoint, json=DATA).status_code == 200
