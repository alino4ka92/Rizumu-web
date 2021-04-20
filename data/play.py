import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Play(SqlAlchemyBase):
    __tablename__ = 'plays'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    beatmap_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('maps.beatmap_id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    score = sqlalchemy.Column(sqlalchemy.Integer)
    accuracy = sqlalchemy.Column(sqlalchemy.Float)
    mark = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    user = orm.relation('User')
    beatmap = orm.relation('Map')
