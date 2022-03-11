import boto3

ses_client = boto3.client("sesv2")


def get_attribute_data(contact_list_name, email):
    """Get the AttributesData for contact `email` in `contact_list_name`"""
    return ses_client.get_contact(ContactListName=contact_list_name, EmailAddress=email)[
        "AttributesData"
    ]


def list_contacts(contact_list_name, topic=None):
    """Yield a lists of not more than 50 contacts in `contact_list_name` for `topic`"""

    def add_contacts(r):
        contacts = []
        for contact in r["Contacts"]:
            contact["AttributesData"] = get_attribute_data(
                contact_list_name, contact["EmailAddress"]
            )
            contacts.append(contact)
        yield contacts

    filter = {}
    if topic is not None:
        filter = {
            "FilteredStatus": "OPT_IN",
            "TopicFilter": {"TopicName": topic, "UseDefaultIfPreferenceUnavailable": True},
        }
    r = ses_client.list_contacts(
        ContactListName=contact_list_name,
        Filter=filter,
        PageSize=50,  # SendBulkEmail operation: You must specify at least 1 destination, and no more than 50 destinations
    )
    yield from add_contacts(r)

    while True:
        token = r.get("NextToken")
        if token is None:
            break
        r = ses_client.list_contacts(ContactListName=contact_list_name, NextToken=token)
        yield from add_contacts(r)


def get_bulk_entries(contacts):
    """Convert a list of contacts to the BulkEmailEntries format for SendBulkEmail"""
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


def send_bulk_email(from_email, contact_list_name, topic, template_name, default_attributes):
    """List contacts in `contact_list_name` for `topic` and send a templated email from `from_email`"""
    # list_contacts yields no more than 50 contacts at a time!
    for contacts in list_contacts(contact_list_name, topic):
        return ses_client.send_bulk_email(
            FromEmailAddress=from_email,
            DefaultContent={
                "Template": {
                    "TemplateName": template_name,
                    "TemplateData": default_attributes,
                }
            },
            BulkEmailEntries=get_bulk_entries(contacts),
        )
