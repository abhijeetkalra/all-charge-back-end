import os
from inspect import getmembers

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mongoengine import MongoEngine

import config

app = Flask(__name__, instance_relative_config=True)
app.url_map.strict_slashes = False
app.config['ERROR_404_HELP'] = False

# register api after creating Flask instance
from views import *

api.init_app(app)


def init(app):
    """
    Init Flask instance, load config
    :param app: Flask instance
    :return: None
    """
    app.config.from_object("config.default")
    if app.env == "development":
        app.config.from_object("config.development")
    elif app.env == "production":
        app.config.from_object("config.production")

    if app.testing:
        app.config.from_object("config.testing")

    init_env(app)

    app.bcrypt = Bcrypt(app)
    app.db = MongoEngine(app)


def init_env(app):
    """
    Update config from environment
    :param app: Flask instance
    :return: None
    """
    envs = [item[0] for item in getmembers(config.default)]
    for env in envs:
        if os.environ.get(env, None):
            app.config[env] = os.environ[env]

    to_int = ['MONGODB_PORT', 'PORT']
    for env in to_int:
        if app.config.get(env, None):
            app.config[env] = int(app.config[env])

    # Some time it's more convenient by providing URI connection
    if app.config.get('MONGODB_URI', None):
        app.config['MONGODB_HOST'] = app.config['MONGODB_URI']
