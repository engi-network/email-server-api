import os

CONTACT_LIST_NAME = os.environ.get("CONTACT_LIST_NAME", "engi-newsletter")
TEMPLATE_NAME = os.environ.get("TEMPLATE_NAME", "engi-newsletter-welcome-template")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "g@engi.network")
