import boto3
from flask import Flask
from flask_restful import Api, Resource, abort, reqparse

app = Flask(__name__)
api = Api(app)
ses_client = boto3.client("sesv2")

parser = reqparse.RequestParser()
parser.add_argument("email", type=str, help="email address")
parser.add_argument("topic", type=str, help="contact list topic")

from flask_restful import Resource, fields, marshal


class Ping(Resource):
    def get(self):
        return "pong"


class Contact(Resource):
    resource_fields = {
        "ResponseMetadata": fields.Raw,
        "ContactListName": fields.Raw,
        "EmailAddress": fields.Raw,
        "TopicDefaultPreferences": fields.Raw,
        "UnsubscribeAll": fields.Raw,
        "CreatedTimestamp": fields.DateTime(dt_format="iso8601"),
        "LastUpdatedTimestamp": fields.DateTime(dt_format="iso8601"),
    }

    def get(self):
        args = parser.parse_args()
        print(f"get {args=}")
        r = ses_client.get_contact(ContactListName=args["topic"], EmailAddress=args["email"])
        return marshal(r, self.resource_fields), r["ResponseMetadata"]["HTTPStatusCode"]

    def post(self):
        args = parser.parse_args()
        print(f"post {args=}")
        return "", 200

    def delete(self):
        args = parser.parse_args()
        print(f"delete {args=}")
        return "", 200


api.add_resource(Ping, "/ping")
api.add_resource(Contact, "/contact")

if __name__ == "__main__":
    app.run(debug=True)
