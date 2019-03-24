#!/usr/bin/python
# encoding: utf-8
"""
api.py

!!DESCRIPTION GOES HERE!!

Copyright (C) University of Oxford 2019
    Ben Goodstein <ben.goodstein at it.ox.ac.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
import os
import click
import json
import psycopg2
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError

class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

DATABASE_URL = os.environ['DATABASE_URL']


auth = HTTPBasicAuth()
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

conn = psycopg2.connect(DATABASE_URL)

USER_DATA = {
    'admin': 'YouShallNotPass'
}

ALBUMS = {}

@app.cli.command()
def resetdb():
    """Destroys and creates the database + tables."""
    print DATABASE_URL
    from sqlalchemy_utils import database_exists, create_database, drop_database
    if database_exists(DATABASE_URL):
        print('Deleting database.')
        drop_database(DATABASE_URL)
    if not database_exists(DATABASE_URL):
        print('Creating database.')
        create_database(DATABASE_URL)

    print('Creating tables.')
    db.create_all()
    print('Shiny!')

@auth.verify_password
def verify(username, password):
    if not(username and password):
        return False
    return USER_DATA.get(username) == password

def message(m):
    return { 'message': m }

class AlbumM(db.Model, Serializer):
    __tablename__ = 'albums'
    __table_args__ = (
        db.UniqueConstraint('artist', 'name', name='unique_artist_album'),
    )
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)

    def __init__(self, artist, name):
        self.artist = artist
        self.name = name

    def serialize(self):
        d = Serializer.serialize(self)
        return d

db.create_all()

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class Album(Resource):
    def get(self, album_id):
        album = AlbumM.query.get(album_id)
        if album:
            return jsonify(album.serialize())
        else:
            return message("Album does not exist"), 404

    @auth.login_required
    def put(self, album_id):
        album = AlbumM.query.get(album_id)
        if album:
            name = request.get_json().get('name')
            artist = request.get_json().get('artist')
            if name:
                album.name = name
            if artist:
                album.artist = artist
            db.session.commit()
            return jsonify(album.serialize())
        else:
            return message("Album does not exist"), 404

    @auth.login_required
    def delete(self, album_id):
        album = AlbumM.query.get(album_id)
        if album:
            db.session.delete(album)
            db.session.commit()
            return message("Album deleted"), 200
        else:
            return message("Album does not exist"), 404

class Albums(Resource):
    decorators = [ limiter.limit("1 per second") ]

    def get(self):
        albums = AlbumM.query.all()
        return jsonify(AlbumM.serialize_list(albums))

    @auth.login_required
    def post(self):
        json_data = request.get_json(force=True)
        try:
            album  = AlbumM(
                    name=json_data['name'],
                    artist=json_data['artist']
                    )
            db.session.add(album)
            db.session.commit()
            print "Count: %i" % db.session.query(AlbumM).count()
            return json.dumps(album.serialize()), 201
        except IntegrityError as e:
            return message("Album already exists"), 409

api.add_resource(HelloWorld, '/api/v1')
api.add_resource(Album, '/api/v1/album/<int:album_id>')
api.add_resource(Albums, '/api/v1/albums')

if __name__ == '__main__':
    app.run(debug=True)
