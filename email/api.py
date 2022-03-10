from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

from contact import Contact
from send import Send
from tasks import add


class Ping(Resource):
    def get(self):
        return "pong"


class Deferred(Resource):
    def get(self):
        add.delay(5, 2)
        return "ok"


api.add_resource(Ping, "/ping")
api.add_resource(Deferred, "/add")
api.add_resource(Contact, "/contact")
api.add_resource(Send, "/send")

if __name__ == "__main__":
    app.run(debug=True)
