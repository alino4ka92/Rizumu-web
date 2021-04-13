from flask import Flask
from data.user import User
from data import db_session
from forms.user import RegisterForm
from flask import Flask, url_for, render_template, request, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user
from forms.user import LoginForm
import flask
from flask import make_response, request
from flask_restful import reqparse, abort, Api, Resource
from data.user_parser import parser

def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")

class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict()})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict() for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            email = args['email'],
            hashed_password = args['hashed_password'],
            created_date = args['created_date']
        )
        session.add(User)
        session.commit()
        return jsonify({'success': 'OK'})