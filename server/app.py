#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)
api = Api(app)

db.init_app(app)

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(rules=('-signups',)) for camper in Camper.query.all()]
        return make_response(campers,200)
    def post(self):
        data = request.get_json()
        try:
            camper = Camper(**data)
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(), 201)
        except Exception as e:
            return make_response({"errors":["validation errors"]}, 400)
api.add_resource(Campers, '/campers')

class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            return make_response(camper.to_dict(),200)
        else:
            return make_response({"error": "Camper not found"}, 404)
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            data = request.get_json()
            try:
                for attr in data:
                    setattr(camper, attr, data[attr])
                db.session.commit()
                return make_response(camper.to_dict(), 202)
            except Exception as e:
                return make_response({"errors":["validation errors"]}, 400)
        else:
            return make_response({"error": "Camper not found"}, 404)

api.add_resource(CamperById, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]
        return make_response(activities,200)
api.add_resource(Activities, '/activities')

class ActivityById(Resource):
    def get(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            return make_response(activity.to_dict(),200)
        else:
            return make_response({"error": "Activity not found"}, 404)
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return make_response({}, 204)
        else:
            return make_response({"error": "Activity not found"}, 404)
api.add_resource(ActivityById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            signup = Signup(**data)
            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(), 201)
        except Exception as e:
            return make_response({"errors":["validation errors"]}, 400)
api.add_resource(Signups, '/signups')


@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)
