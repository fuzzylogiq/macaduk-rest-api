#!/bin/bash


heroku pg:reset DATABASE --confirm desolate-journey-49620
git commit --allow-empty -m "empty commit"
git push heroku master
