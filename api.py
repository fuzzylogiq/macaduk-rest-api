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

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

auth = HTTPBasicAuth()
app = Flask(__name__)
api = Api(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

USER_DATA = {
    'admin': 'YouShallNotPass'
}

todos = {}

@auth.verify_password
def verify(username, password):
    if not(username and password):
        return False
    return USER_DATA.get(username) == password

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class TodoSimple(Resource):
    decorators = [ limiter.limit("1 per second") ]

    def get(self, todo_id):
        return {todo_id: todos[todo_id]}

    @auth.login_required
    def put(self, todo_id):
        print request.headers
        todos[todo_id] = {'detail': request.form['detail'],
                          'date': request.form['date']
                          }
        return {todo_id: todos[todo_id]}




api.add_resource(HelloWorld, '/')
api.add_resource(TodoSimple, '/todo/<int:todo_id>')
if __name__ == '__main__':
    app.run(debug=True)
