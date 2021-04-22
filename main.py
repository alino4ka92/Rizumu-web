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
import random
import datetime as dt

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


@app.route('/')
@app.route('/index')  # /index перенаправляет пользователя на страницу с картами
def index():
    return redirect('/maps')


@app.route('/register', methods=['GET', 'POST'])
def reqister():  # форма регистрации
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
def login():  # форма авторизации
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


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):  # страница с профилем пользователя
    if request.method == 'GET':
        sess = db_session.create_session()
        ans = sess.query(User).filter(User.id == user_id)
        if not ans:
            return render_template("404.html", message='Ничего не найдено')
        user = ans[0]
        plays = user.plays
        plays.sort(key=lambda x: x.date, reverse=True)
        marks_colors = {'S': "#ffeec2", "SS": "#ffeec2", "A": "#c8ffbf", "B": "#a8c5ff", "C": "#efb0ff", "D": "#ffb0b0"}
        return render_template("profile.html", user=user, plays=plays, marks_colors=marks_colors)
    elif request.method == 'POST':  # обновление аватарки
        f = request.files['file']
        f.save(f'static/img/avatars/{user_id}.png')
        sess = db_session.create_session()
        user = sess.query(User).filter(User.id == user_id).all()[0]
        user.avatar = f'{user_id}.png'
        sess.commit()
        print(user)
        return redirect(f'/profile/{user_id}')


@app.route('/maps/')  # страница со всеми картами
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
        # users = sess.query(User).filter(User.name.like(f'%{query}%'))
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


@app.route('/maps/<int:map_id>')  # страница с одной картой
def map(map_id):
    sess = db_session.create_session()
    ans = sess.query(Map).filter(Map.beatmap_id == map_id)
    if not ans:
        return render_template("404.html", message='Ничего не найдено')
    map = ans[0]
    plays = map.plays

    plays.sort(key=lambda x: x.score, reverse=True)
    if len(plays) > 50:
        plays = plays[:50]
    marks_colors = {'S': "ffeec2", "SS": "ffeec2", "A": "c8ffbf", "B": "a8c5ff", "C": "efb0ff", "D": "ffb0b0"}
    return render_template("map.html", map=map, plays=plays, marks_colors=marks_colors)


@blueprint.route('/api/synchronization/<string:email>;<string:password>')  # получение игрой рекордов пользователя
def synchronization(email, password):
    sess = db_session.create_session()
    user = sess.query(User).filter(User.email == email).first()
    if not user:
        return jsonify({
            'result': 0
        })
    if not user.check_password(password):
        return jsonify({
            'result': 0
        })
    while True:
        key = generate_key()
        if not sess.query(User).filter(User.secret_key == key).first():
            break
    user.secret_key = key
    sess.commit()
    records = sess.query(Play).filter(Play.user_id == user.id).all()
    return jsonify({
        'result': 1,
        'records': [(i.beatmap_id, i.score, i.accuracy, i.combo, i.mark) for i in records],
        'key': key,
        'user_id': user.id
    })


@blueprint.route('/api/get_records/', methods=['POST'])  # добавление рекорда
def get_records():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    sess = db_session.create_session()
    us_id = request.json['user_id']
    user = sess.query(User).filter(User.id == us_id).first()
    if user.secret_key == request.json['key']:
        for pl in request.json['records']:
            play = sess.query(Play).filter(Play.beatmap_id == pl[0], Play.user_id == us_id,
                                           Play.score == pl[1], Play.accuracy == pl[2],
                                           Play.combo == pl[3], Play.mark == pl[4]).first()
            if not play:
                pl = Play(beatmap_id=pl[0], user_id=us_id, score=pl[1], accuracy=pl[2],
                          combo=pl[3], mark=pl[4], date=dt.datetime.now())
                sess.add(pl)
        sess.commit()
    return jsonify({'error': 'Incorrect key'})


def generate_key():  # генерация ключа для авторизации пользователя из игры
    chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    key = ''.join([random.choice(chars) for _ in range(30)])
    return key


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
