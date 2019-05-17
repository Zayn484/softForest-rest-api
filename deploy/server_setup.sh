#!/usr/bin/env bash

set -e

# TODO: Set to URL of git repo.
PROJECT_GIT_URL='https://github.com/Zayn484/softforest-rest-api.git'

PROJECT_BASE_PATH='/usr/local/apps'
VIRTUALENV_BASE_PATH='/usr/local/virtualenvs'

# Set Ubuntu Language
locale-gen en_GB.UTF-8

# Install Python, SQLite and pip
echo "Installing dependencies..."
apt-get update
apt-get install -y python3-dev python3-venv sqlite python-pip supervisor nginx git
apt-get install redis
apt install daphne

mkdir -p $PROJECT_BASE_PATH
git clone $PROJECT_GIT_URL $PROJECT_BASE_PATH/softforest-rest-api

mkdir -p $VIRTUALENV_BASE_PATH
python3 -m venv $VIRTUALENV_BASE_PATH/softforest

$VIRTUALENV_BASE_PATH/softforest/bin/pip install -r $PROJECT_BASE_PATH/softforest-rest-api/requirements.txt

# Run migrations
cd $PROJECT_BASE_PATH/softforest-rest-api/src

# Setup Supervisor to run our uwsgi process.
cp $PROJECT_BASE_PATH/softforest-rest-api/deploy/supervisor_softforest_api.conf /etc/supervisor/conf.d/softforest.conf
supervisorctl reread
supervisorctl update
supervisorctl restart all

# Setup nginx to make our application accessible.
cp $PROJECT_BASE_PATH/softforest-rest-api/deploy/nginx_softforest_api.conf /etc/nginx/sites-available/softforest.conf
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/softforest.conf /etc/nginx/sites-enabled/softforest.conf
systemctl restart nginx.service

echo "DONE! :)"
