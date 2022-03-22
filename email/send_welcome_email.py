import boto3

from default_params import CONTACT_LIST_NAME, FROM_EMAIL, TEMPLATE_NAME

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
