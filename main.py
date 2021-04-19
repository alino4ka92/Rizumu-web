from flask import Flask
from data.user import User
from data.map import Map, read_maps
import os
from data.play import Play
from data import db_session
from flask import Flask, url_for, render_template, request, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
import flask
from flask import make_response, request
from flask_restful import reqparse, abort, Api, Resource
from forms.user import RegisterForm, LoginForm
from requests import get, post, delete
from data.user_resources import UserResource, UserListResource
app = Flask(__name__)
blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/test_visual')
def test_visual():
    return render_template('base.html', title="1")


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html', title="1")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@blueprint.route('/api/change_avatar/<int:user_id>')
def change_avatar(user_id):
    if current_user['id'] != user_id:
        return render_template('404.html', message='Пользователь не залогинен')


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    if request.method == 'GET':
        sess = db_session.create_session()
        ans = sess.query(User).filter(User.id==user_id)
        if not ans:
            return render_template("404.html", message='Ничего не найдено')
        user = ans[0]
        plays = user.plays
        plays.sort(key=lambda x:x.date)
        marks_colors= {'S': "#ffeec2", "SS" :"ffeec2", "A": "c8ffbf", "B": "a8c5ff", "C": "efb0ff", "D":"ffb0b0"}
        return render_template("profile.html", user=user, plays=plays, marks_colors=marks_colors)
    elif request.method == 'POST':
        f = request.files['file']
        f.save(f'static/img/avatars/{user_id}.png')
        sess = db_session.create_session()
        user = sess.query(User).filter(User.id==user_id).all()[0]
        user.avatar = f'{user_id}.png'
        sess.commit()
        print(user)
        return redirect(f'/profile/{user_id}')

@app.route('/maps/')
def maps():
    read_maps()
    map = []
    sess = db_session.create_session()
    for mp in sess.query(Map).all():
        map.append(mp)

    return render_template("maps.html", maps=map, title="Карты")

@app.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        sess = db_session.create_session()
        #users = sess.query(User).filter(User.name.like(f'%{query}%'))
        return render_template('users.html')
    elif request.method == 'POST':
        query = request.form['name']
        sess = db_session.create_session()
        users = sess.query(User).filter(User.name.like(f'%{query}%')).all()
        message = ''
        if len(users) == 0:
            message = 'По вашему запросу ничего не найдено...'
        else:
            message = f"Найдено {len(users)} пользователей: "
        return render_template('users.html', users=users, message=message)
@app.route('/maps/<int:map_id>')
def map(map_id):
    sess = db_session.create_session()
    ans = sess.query(Map).filter(Map.id==map_id)
    if not ans:
        return render_template("404.html", message='Ничего не найдено')
    map = ans[0]
    plays = map.plays
    if len(plays)>50:
        plays = plays[:50]
    plays.sort(key=lambda x: x.score)
    marks_colors = {'S': "ffeec2", "SS": "ffeec2", "A": "c8ffbf", "B": "a8c5ff", "C": "efb0ff", "D": "ffb0b0"}
    return render_template("map.html", map=map, plays=plays, marks_colors=marks_colors)
def main():

    db_session.global_init("db/rizumu.db")
    app.register_blueprint(blueprint)
    api.add_resource(UserResource, '/api/user/<int:user_id>')
    api.add_resource(UserListResource, '/api/user')

    read_maps()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)




if __name__ == '__main__':
    main()
