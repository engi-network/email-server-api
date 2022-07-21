import json

import boto3

from default_params import (
    CONTACT_US_EMAIL,
    CONTACT_US_RESPONSE_TEMPLATE_NAME,
    CONTACT_US_TEMPLATE_NAME,
    FROM_EMAIL,
)

ses_client = boto3.client("sesv2")


def send_contact_us_email(from_addr, first_name, last_name, subject, message):
    # send a message to us using the information provided on the contact form
    # you gotta be real careful with template interpolation
    # if the template contains variable that are not defined in the TemplateData arg
    # the email will silently fail to send
    ses_client.send_email(
        FromEmailAddress=FROM_EMAIL,
        Destination={
            "ToAddresses": [
                CONTACT_US_EMAIL,
            ],
        },
        Content={
            "Template": {
                "TemplateName": CONTACT_US_TEMPLATE_NAME,
                "TemplateData": json.dumps(
                    {
                        "email": from_addr,
                        "first_name": first_name,
                        "last_name": last_name,
                        "subject": subject,
                        "message": message,
                    }
                ),
            },
        },
    )
    # send a confirmation email to the customer
    ses_client.send_email(
        FromEmailAddress=CONTACT_US_EMAIL,
        Destination={
            "ToAddresses": [
                from_addr,
            ],
        },
        Content={
            "Template": {
                "TemplateName": CONTACT_US_RESPONSE_TEMPLATE_NAME,
                "TemplateData": json.dumps(
                    {
                        "first_name": first_name,
                        "subject": subject,
                    }
                ),
            },
        },
    )
