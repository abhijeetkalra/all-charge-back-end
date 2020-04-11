from functools import wraps

import jwt
from flask import request, g
from jwt import InvalidTokenError

from app import app
from models import User
from util import abort


def encode_user_token(id):
    """
    Generate user token
    :param userid: userid
    :return: user jwt token
    """
    data = {
        'user': {
            'id': id
        },
        'type': 'user'
    }

    return jwt.encode(data, key=app.secret_key, algorithm='HS256')


def decode_token(token):
    """
    Try to decode token, or return 401
    :param token: token from request
    :return: decoded token or 401
    """
    try:
        return jwt.decode(token, key=app.secret_key, algorithms='HS256')
    except InvalidTokenError:
        abort(401, "Invalid token")


def normalize_token(token):
    """
    Normalize token, will be useful when there are different token types
    :param token: decoded token
    :return: normalized token
    """
    if token is None or "type" not in token:
        return token
    if token["type"] == "user":
        return enrich_user_token(token)

    return token


def enrich_user_token(token):
    """
    Add more information for user token
    :param token: decoded user token
    :return: enriched token
    """
    if not ("user" in token and "id" in token["user"]):
        abort(401, "Invalid token")

    user_id = token["user"]["id"]

    user = User.objects(id=user_id).first()

    if not user:
        abort(401, "Invalid user")

    token['user']['role'] = user['role']
    token['user']['active'] = user['active']
    token['user']['email'] = user['email']
    token['user']['username'] = user['username']
    return token


def get_token():
    """
    Get auth token from request
    :return: token or None
    """
    auth = dict(request.headers).get('Authorization', None)
    if not auth:
        return None

    if auth.startswith("token ") or auth.startswith("bearer ") or auth.startswith("Bearer "):
        token = auth.split(" ")[1]
        return decode_token(token.encode('utf8'))

    app.logger.warn('Invalid auth header format')
    return None


@app.before_request
def before_request():
    """
    Add decoded token to global variable g, for later use
    :return: None
    """
    g.token = normalize_token(get_token())


def token_required(type=None):
    """
    Decorator used to check expected token type
    :param type: list of expected token type
    :return: Allow or 401
    """
    def decorate(func):
        @wraps(func)
        def check_token(*args, **kwargs):
            if not g.token:
                abort(401, "Not Authorized")
            if isinstance(type, list):
                if g.token.get('type', None) not in type:
                    abort(401, "Not Authorized")
            return func(*args, **kwargs)

        return check_token

    return decorate


def allow_roles(roles):
    """
    Decorator used to check user roles
    :param roles: list of expected user role
    :return: Allow or 403
    """
    def decorate(func):
        @wraps(func)
        def check_token(*args, **kwargs):
            if not g.token:
                abort(403, "Access Denied")

            if g.token.get('user', {}).get('role', None) in roles:
                return func(*args, **kwargs)

            abort(403, "Access Denied")

        return check_token

    return decorate
