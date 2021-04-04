from flask import Flask
from data.user import User
from data import db_session
from flask import Flask, url_for, render_template, request, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user
import flask
from flask import make_response, request
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/rizumu.db")
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
