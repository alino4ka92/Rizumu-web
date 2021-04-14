import datetime
import sqlalchemy
import pygame
import os
from data import db_session
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm.exc import NoResultFound
class Map(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'maps'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    artist = sqlalchemy.Column(sqlalchemy.String)
    creator = sqlalchemy.Column(sqlalchemy.String)
    version = sqlalchemy.Column(sqlalchemy.String)
    image = sqlalchemy.Column(sqlalchemy.String, default="default.png")
    music = sqlalchemy.Column(sqlalchemy.String, default="default.mp3")
    added_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())


def read_maps():
    songs = os.listdir(path="static/maps")
    maps = []
    sess = db_session.create_session()
    for song in songs:
        file_names = os.listdir(path=f'static/maps/{song}')
        diffs = [diff for diff in file_names if diff.endswith('.osu')]
        for diff in diffs:
            file = open(f'static\\maps\\{song}\\{diff}', encoding="utf-8").read().split(
                '\n')
            dir = song
            general_line = file.index('[General]')
            general = {}
            cur_line = general_line + 1
            while file[cur_line].lstrip() != '':
                current = file[cur_line]
                tag = current[:current.find(':')]
                info = current[current.find(':') + 1:]
                general[tag] = info.lstrip()
                cur_line += 1

            metadata_line = file.index('[Metadata]')
            metadata = {}
            cur_line = metadata_line + 1
            while file[cur_line].lstrip() != '':
                current = file[cur_line]
                tag = current[:current.find(':')]
                info = current[current.find(':') + 1:]
                metadata[tag] = info.lstrip()
                cur_line += 1

            events_line = file.index('[Events]')
            events = []
            cur_line = events_line + 1
            while file[cur_line].lstrip() != '':
                current = file[cur_line]
                current = current.split(',')
                current = [i.lstrip() for i in current]
                events.append(current)
                cur_line += 1

            name = metadata['Title']
            artist = metadata['Artist']
            creator = metadata['Creator']
            version = metadata['Version']
            music = f"/static/maps/{dir}/{general['AudioFilename']}"
            mp = sess.query(Map).filter(Map.name == name, Map.artist == artist,
                                        Map.creator == creator, Map.version == version,
                                        Map.music == music)
            try:
                model = mp.one()
                continue
            except NoResultFound:
                for elem in events:
                    event_type, *another = elem
                    if event_type == '0':
                        c, background_file, x_offset, y_offset = another
                        background_file = background_file.rstrip('"').lstrip('"')
                        background = pygame.image.load(f'static/maps/{dir}/{background_file}')
                        path = f"static/img/maps/{background_file}.png"
                        pygame.image.save(pygame.transform.smoothscale(background, (200, 160)), path)
                map = Map(name=name, artist=artist, creator=creator, version=version, music=music,
                          image=path)
                sess.add(map)
        sess.commit()