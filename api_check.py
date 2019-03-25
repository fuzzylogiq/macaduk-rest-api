#!/usr/bin/python
# encoding: utf-8
"""
api_check.py

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

import sys, json, time, curses
import requests
from playsound import playsound
from collections import Counter
from curses import COLOR_WHITE, COLOR_RED
import subprocess

GOAL = 260

stdscr = curses.initscr()
curses.curs_set(0)
curses.start_color()
curses.use_default_colors()
curses.init_pair(1, COLOR_WHITE, COLOR_RED)
prev_most = ""
sounds_played = []

def say(what):
    command = "say %s" % what
    process = subprocess.Popen(command.split())
while True:
    r = requests.get('https://restapis.tk/api/v1/albums')
    if r.status_code == 200:
        albums = r.json()
        count = len(albums)
        most = ""
        second = ""
        cpair = 0
        mod = count % 100

        if count > 0:
            counter = Counter([k['artist'] for k in albums]).most_common(2)
            most = counter[0][0]
            try:
                second = counter[1][0]
            except IndexError:
                pass
        if count > GOAL:
            cpair = 1
        stdscr.refresh()
        stdscr.addstr(0, 0, "Total Albums: %i" % count, curses.color_pair(cpair))
        stdscr.addstr(1, 0, "Most Popular: %s" % most)
        stdscr.addstr(2, 0, "Second: %s" % second)
        stdscr.refresh()
        if count > GOAL and "goal" not in sounds_played:
            playsound('klaxon.wav', block=False)
            sounds_played.append("goal")
        if most and most != prev_most:
            #playsound('ding.wav', block=False)
            say("%s now the most popular artist" % most)
            prev_most = most
        if mod == 0 and count not in sounds_played and count != 0:
            #playsound('%i.wav' % count, block=False)
            say('%i albums added' % count)
            sounds_played.append(count)
        stdscr.erase()
        time.sleep(1)



