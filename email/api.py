import boto3
from flask import Flask
from flask_restful import Api, Resource, abort, fields
from flask_restful import marshal as _marshal
from flask_restful import reqparse

app = Flask(__name__)
api = Api(app)
ses_client = boto3.client("sesv2")

parser = reqparse.RequestParser()
parser.add_argument("email", type=str, help="email address")
parser.add_argument("contact_list_name", type=str, help="contact list name")
parser.add_argument("topics", action="append", help="list of topics")
parser.add_argument(
    "attributes", type=str, default="", help="contact attributes encoded as string"
)


class Ping(Resource):
    def get(self):
        return "pong"


def marshal(r):
    resource_fields = {
        "ResponseMetadata": fields.Raw,
        "ContactListName": fields.Raw,
        "EmailAddress": fields.Raw,
        "TopicDefaultPreferences": fields.Raw,
        "AttributesData": fields.Raw,
        "TopicPreferences": fields.Raw,
        "UnsubscribeAll": fields.Raw,
        "CreatedTimestamp": fields.DateTime(dt_format="iso8601"),
        "LastUpdatedTimestamp": fields.DateTime(dt_format="iso8601"),
    }
    return _marshal(r, resource_fields), r["ResponseMetadata"]["HTTPStatusCode"]


class Contact(Resource):
    def get(self):
        """Get an existing `email` on list `contact_list_name`"""
        args = parser.parse_args()
        app.logger.info(f"getting {args=}")
        try:
            return marshal(
                ses_client.get_contact(
                    ContactListName=args["contact_list_name"], EmailAddress=args["email"]
                )
            )
        except ses_client.exceptions.NotFoundException:
            abort(404, message="not found")

    def post(self):
        """Create a new `email` on list `contact_list_name`"""
        args = parser.parse_args()
        app.logger.info(f"adding {args=}")
        try:
            return marshal(
                ses_client.create_contact(
                    ContactListName=args["contact_list_name"],
                    EmailAddress=args["email"],
                    TopicPreferences=[
                        {"TopicName": topic, "SubscriptionStatus": "OPT_IN"}
                        for topic in args.get("topics", [])
                    ],
                    AttributesData=args.get("attributes", ""),
                )
            )
        except ses_client.exceptions.AlreadyExistsException:
            abort(409, message="already exists")

    def delete(self):
        """Delete `email` from list `contact_list_name`"""
        args = parser.parse_args()
        app.logger.info(f"deleting {args=}")
        try:
            return marshal(
                ses_client.delete_contact(
                    ContactListName=args["contact_list_name"], EmailAddress=args["email"]
                )
            )
        except ses_client.exceptions.NotFoundException:
            abort(404, message="not found")


send_parser = parser.copy()
send_parser.add_argument("template_name", type=str, help="template name", required=True)
send_parser.add_argument("from_email", type=str, help="from address", required=True)


class Send(Resource):
    def post(self):
        """Send a templated mass email from `from_email` to `contact_list_name`"""
        args = send_parser.parse_args()
        app.logger.info(f"sending to {args=}")
        return "", 200


api.add_resource(Ping, "/ping")
api.add_resource(Contact, "/contact")
api.add_resource(Send, "/send")

if __name__ == "__main__":
    app.run(debug=True)
