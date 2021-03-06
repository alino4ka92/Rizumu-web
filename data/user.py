import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):  # класс пользователя
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    avatar = sqlalchemy.Column(sqlalchemy.String, default="default.png")
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    plays = orm.relation("Play", back_populates="user")
    friends = sqlalchemy.Column(sqlalchemy.String, default="")
    secret_key = sqlalchemy.Column(sqlalchemy.String, default="-")

    # функции для хеширования пароля
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
