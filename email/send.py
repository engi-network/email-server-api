from flask import current_app as app
from flask_restful import Resource, reqparse


def get_attribute_data(client, contact_list, email):
    return client.get_contact(ContactListName=contact_list, EmailAddress=email)["AttributesData"]


def list_contacts(client, contact_list, topic=None):
    contacts = []

    def add_contacts(r):
        for contact in r["Contacts"]:
            contact["AttributesData"] = get_attribute_data(
                client, contact_list, contact["EmailAddress"]
            )
            contacts.append(contact)

    filter = {}
    if topic is not None:
        filter = {
            "FilteredStatus": "OPT_IN",
            "TopicFilter": {"TopicName": topic, "UseDefaultIfPreferenceUnavailable": True},
        }
    r = client.list_contacts(
        ContactListName=contact_list,
        Filter=filter,
    )
    add_contacts(r)

    while True:
        token = r.get("NextToken")
        if token is None:
            break
        r = client.list_contacts(ContactListName=contact_list, NextToken=token)
        add_contacts(r)

    return contacts


def get_bulk_entries(contacts):
    entries = []
    for c in contacts:
        entries.append(
            {
                "Destination": {
                    "ToAddresses": [
                        c["EmailAddress"],
                    ],
                },
                "ReplacementEmailContent": {
                    "ReplacementTemplate": {"ReplacementTemplateData": c["AttributesData"]}
                },
            }
        )
    return entries


def send_bulk_email(client, from_email, contact_list, topic, template_name, default_attributes):
    contacts = list_contacts(client, contact_list, topic)
    # TODO remove me!
    entries = [
        e for e in get_bulk_entries(contacts) if "kelly" in e["Destination"]["ToAddresses"][0]
    ]
    return client.send_bulk_email(
        FromEmailAddress=from_email,
        DefaultContent={
            "Template": {
                "TemplateName": template_name,
                "TemplateData": default_attributes,
            }
        },
        BulkEmailEntries=entries,
    )


parser = reqparse.RequestParser()
parser.add_argument("contact_list_name", type=str, help="contact list name", required=True)
parser.add_argument("template_name", type=str, help="template name", required=True)
parser.add_argument("from_email", type=str, help="from address", required=True)
parser.add_argument("default_attributes", type=str, help="default attributes", required=True)
parser.add_argument("topic", type="str", help="topic to filter contacts", required=True)


class Send(Resource):
    def post(self):
        """Send a templated mass email from `from_email` to `contact_list_name`"""
        args = parser.parse_args()
        app.logger.info(f"sending to {args=}")
        return "", 200
