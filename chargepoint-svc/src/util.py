import os
import logging
from flask import jsonify
from flask_restplus import abort as flask_rest_abort

from app import app


def encrypt_passwd(password):
    return app.bcrypt.generate_password_hash(password).decode('utf-8')


def check_password(pw_hash, password):
    return app.bcrypt.check_password_hash(pw_hash, password)


def OK(message, payload=None):
    d = {'message': message}

    if payload:
        d.update(payload)

    return jsonify(d)


def abort(code, message=None):
    flask_rest_abort(code, message=message, status=code)



logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level=logging.ERROR
)


def get_log_level():
    l = os.environ.get('LOG_LEVEL', 'info')

    if l == 'debug':
        return logging.DEBUG
    elif l == 'info':
        return logging.INFO
    elif l == 'warning':
        return logging.WARNING

    return logging.ERROR


def get_env(name):
    if name not in os.environ:
        raise Exception("%s not set" % name)
    return os.environ[name]

def get_logger(name):
    l = logging.getLogger(name)
    l.setLevel(get_log_level())
    return l