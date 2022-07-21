from flask import current_app as app
from flask_restful import Resource, reqparse

from default_params import CONTACT_US_EMAIL, CONTACT_US_TEMPLATE_NAME, FROM_EMAIL
from tasks import async_send_contact_us_email

parser = reqparse.RequestParser()
parser.add_argument("email", type=str, help="email address")
parser.add_argument("first_name", type=str, help="first name")
parser.add_argument("last_name", type=str, help="last name")
parser.add_argument("subject", type=str, help="message subject")
parser.add_argument("message", type=str, help="message")


class ContactUs(Resource):
    def post(self):
        """Process the Contact Us form on the website"""
        args = parser.parse_args()
        app.logger.info(
            f"sending from {FROM_EMAIL=} to {CONTACT_US_EMAIL=} using template {CONTACT_US_TEMPLATE_NAME=} {args=}"
        )
        task = async_send_contact_us_email.delay(
            args["email"], args["first_name"], args["last_name"], args["subject"], args["message"]
        )
        return task.id, 202
