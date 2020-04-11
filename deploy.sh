#!/bin/sh

docker build -t flask-heroku:latest .
heroku container:push web
heroku container:release web 