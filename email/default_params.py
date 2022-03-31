import os

CONTACT_LIST_NAME = os.environ.get("CONTACT_LIST_NAME", "engi-newsletter")
TEMPLATE_NAME = os.environ.get("TEMPLATE_NAME", "engi-newsletter-welcome-template")
EMAIL = os.environ["EMAIL"]
FROM_EMAIL = os.environ.get("FROM_EMAIL", EMAIL)
TOPICS = [CONTACT_LIST_NAME, "engi-programmer", "engi-business", "engi-investor", "engi-curious"]
