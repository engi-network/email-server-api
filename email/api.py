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
parser.add_argument("topic", type=str, help="contact list topic")


class Ping(Resource):
    def get(self):
        return "pong"


def marshal(r):
    resource_fields = {
        "ResponseMetadata": fields.Raw,
        "ContactListName": fields.Raw,
        "EmailAddress": fields.Raw,
        "TopicDefaultPreferences": fields.Raw,
        "UnsubscribeAll": fields.Raw,
        "CreatedTimestamp": fields.DateTime(dt_format="iso8601"),
        "LastUpdatedTimestamp": fields.DateTime(dt_format="iso8601"),
    }
    return _marshal(r, resource_fields), r["ResponseMetadata"]["HTTPStatusCode"]


class Contact(Resource):
    def get(self):
        """Get an existing `email` on list `topic`"""
        args = parser.parse_args()
        app.logger.info(f"getting {args=}")
        try:
            return marshal(
                ses_client.get_contact(ContactListName=args["topic"], EmailAddress=args["email"])
            )
        except ses_client.exceptions.NotFoundException:
            abort(404, message="not found")

    def post(self):
        """Create a new `email` on list `topic`"""
        args = parser.parse_args()
        app.logger.info(f"adding {args=}")
        try:
            return marshal(
                ses_client.create_contact(
                    ContactListName=args["topic"], EmailAddress=args["email"]
                )
            )
        except ses_client.exceptions.AlreadyExistsException:
            abort(409, message="already exists")

    def delete(self):
        """Delete `email` from list `topic`"""
        args = parser.parse_args()
        app.logger.info(f"deleting {args=}")
        try:
            return marshal(
                ses_client.delete_contact(
                    ContactListName=args["topic"], EmailAddress=args["email"]
                )
            )
        except ses_client.exceptions.NotFoundException:
            abort(404, message="not found")


api.add_resource(Ping, "/ping")
api.add_resource(Contact, "/contact")

if __name__ == "__main__":
    app.run(debug=True)
