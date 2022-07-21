import os

EMAIL = os.environ["EMAIL"]
FROM_EMAIL = os.environ.get("FROM_EMAIL", EMAIL)
CONTACT_LIST_NAME = os.environ.get("CONTACT_LIST_NAME", "engi-newsletter")
TEMPLATE_NAME = os.environ.get("TEMPLATE_NAME", "engi-newsletter-welcome-template")
CONTACT_US_EMAIL = os.environ.get("CONTACT_US_EMAIL", "contact@engi.network")
CONTACT_US_TEMPLATE_NAME = os.environ.get("CONTACT_US_TEMPLATE_NAME", "engi-contact-us-template")
CONTACT_US_RESPONSE_TEMPLATE_NAME = os.environ.get(
    "CONTACT_US_RESPONSE_TEMPLATE_NAME", "engi-contact-us-response-template"
)
TEST_TOPIC = "engi-test"
TOPICS = [CONTACT_LIST_NAME, "engi-programmer", "engi-business", "engi-investor", "engi-curious"]
