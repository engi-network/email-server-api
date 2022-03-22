import json
import os

import boto3

CONTACT_LIST_NAME = os.environ.get("CONTACT_LIST_NAME", "engi-newsletter")
TEMPLATE_NAME = os.environ.get("TEMPLATE_NAME", "engi-newsletter-welcome-template")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "g@engi.network")


ses_client = boto3.client("sesv2")


def send_welcome_email(to_addr, attributes):
    return ses_client.send_email(
        FromEmailAddress=FROM_EMAIL,
        Destination={
            "ToAddresses": [
                to_addr,
            ],
        },
        Content={
            "Template": {
                "TemplateName": TEMPLATE_NAME,
                "TemplateData": attributes,
            },
        },
        ListManagementOptions={
            "ContactListName": CONTACT_LIST_NAME,
            "TopicName": CONTACT_LIST_NAME,
        },
    )
