import boto3
from flask import current_app as app
from flask_restful import Resource, abort, fields
from flask_restful import marshal as _marshal
from flask_restful import reqparse
from flask_restful.inputs import boolean

from default_params import CONTACT_LIST_NAME, TOPICS
from tasks import async_send_welcome_email

ses_client = boto3.client("sesv2")

parser = reqparse.RequestParser()
parser.add_argument("email", type=str, help="email address")
parser.add_argument(
    "contact_list_name", default=CONTACT_LIST_NAME, type=str, help="contact list name"
)
parser.add_argument("topics", action="append", default=TOPICS, help="list of topics")
parser.add_argument(
    "attributes", type=str, default="{}", help="contact attributes encoded as string"
)
parser.add_argument(
    "unsubscribe_all", type=boolean, default=False, help="unsubscribe contact from all list topics"
)
parser.add_argument("topics_unsubscribe", action="append", help="list of topics to unsubscribe")
parser.add_argument(
    "send_welcome_email", type=boolean, default=True, help="send welcome email on subscribe"
)
# for ContactUs
parser.add_argument("first_name", type=str, help="first name")
parser.add_argument("last_name", type=str, help="last name")
parser.add_argument("subject", type=str, help="message subject")
parser.add_argument("message", type=str, help="message")


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


def get_topics(topics, subscribe=True):
    if not topics:
        return []
    s = "IN" if subscribe else "OUT"
    return [{"TopicName": topic, "SubscriptionStatus": f"OPT_{s}"} for topic in topics]


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
        attrs = args.get("attributes", "")
        email = args["email"]
        try:
            r = marshal(
                ses_client.create_contact(
                    ContactListName=args["contact_list_name"],
                    EmailAddress=email,
                    TopicPreferences=get_topics(args.get("topics", [])),
                    AttributesData=attrs,
                )
            )
            if args.get("send_welcome_email", True):
                app.logger.info(f"sending welcome email to {email=} {attrs=}")
                async_send_welcome_email.delay(email, attrs)
            return r
        except ses_client.exceptions.AlreadyExistsException:
            abort(409, message="already exists")

    def put(self):
        """Update an existing contact `email` on list `contact_list_name`"""
        args = parser.parse_args()
        app.logger.info(f"updating {args=}")
        kwargs = dict(
            ContactListName=args["contact_list_name"],
            EmailAddress=args["email"],
            TopicPreferences=get_topics(args.get("topics", []))
            + get_topics(args.get("topics_unsubscribe", []), subscribe=False),
            UnsubscribeAll=args.get("unsubscribe_all", False),
        )
        attributes = args.get("attributes")

        try:
            if attributes:
                kwargs["AttributesData"] = attributes
            else:
                # this is annoying -- need to supply AttributesData else it gets set to None
                r = ses_client.get_contact(
                    ContactListName=args["contact_list_name"], EmailAddress=args["email"]
                )
                kwargs["AttributesData"] = r["AttributesData"]
            app.logger.info(f"{kwargs=}")
            return marshal(ses_client.update_contact(**kwargs))
        except ses_client.exceptions.NotFoundException:
            abort(404, message="not found")

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
