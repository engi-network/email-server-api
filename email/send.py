from flask import current_app as app
from flask_restful import Resource, reqparse

from tasks import async_send_bulk_email

parser = reqparse.RequestParser()
parser.add_argument("contact_list_name", type=str, help="contact list name", required=True)
parser.add_argument("template_name", type=str, help="template name", required=True)
parser.add_argument("from_email", type=str, help="from address", required=True)
parser.add_argument("default_attributes", type=str, help="default attributes", required=True)
parser.add_argument("topic", type=str, help="topic to filter contacts", required=True)


class Send(Resource):
    def post(self):
        """Send a templated mass email from `from_email` to `contact_list_name`"""
        args = parser.parse_args()
        app.logger.info(f"sending to {args=}")
        async_send_bulk_email.delay(
            args["from_email"],
            args["contact_list_name"],
            args["topic"],
            args["template_name"],
            args["default_attributes"],
        )
