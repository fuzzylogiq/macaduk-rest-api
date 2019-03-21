#!/usr/bin/python
# encoding: utf-8
"""
attack-api.py

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

import urllib2
import json
import base64
import time
import json

username = 'admin'
password = 'YouShallNotPass'
url = 'http://127.0.0.1:5000/todo'

def add_auth(request):
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    return request

i = 1
while True:
    data = "detail='todo number %s'&date='13/23/51'"
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
    request = urllib2.Request(url + '/' + str(i), data=data)
    request.get_method = lambda: 'PUT'
    request = add_auth(request)
    result = opener.open(request)
    print result.read()
    i = i + 1
    time.sleep(1)



