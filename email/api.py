from flask import Flask
from flask_restful import Api, Resource, abort, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("email", type=str, help="email address")
parser.add_argument("topic", type=str, help="contact list topic")


class Ping(Resource):
    def get(self):
        return "pong"


class Contact(Resource):
    def get(self):
        args = parser.parse_args()
        return "", 200

    def post(self):
        args = parser.parse_args()
        return "", 200


api.add_resource(Ping, "/ping")
api.add_resource(Contact, "/contact")

if __name__ == "__main__":
    app.run(debug=True)
