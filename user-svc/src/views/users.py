import re
import uuid
from flask import request, g
from flask_restplus import fields, Resource

from . import api
from auth.token import token_required, encode_user_token
from models import User
from util import encrypt_passwd, abort, OK

ns = api.namespace("User",
                   path='/user',
                   description='user management')

user_roles = ["user", "admin"]

user_create_model = api.model('UserCreateModel', {
    'password': fields.String(required=True),
    'email': fields.String(required=True),
    'username': fields.String(required=True)
})

user_model = api.model('UserModel', {
    'id': fields.String,
    'email': fields.String,
    'username': fields.String,
    'active': fields.Boolean,
    'role': fields.String(enum=user_roles)
})


def check_username(username):
    """
    Validate username
    :param username: username
    :return: True or False
    """
    if not username.isalnum():
        return False, "Username is not alphanumeric"

    if len(username) > 20:
        return False, "Username length must be less than 20"

    return True, "Valid username"


def check_password(password):
    """
    Validate password pattern
    :param password: password
    :return: True or False
    """
    if not 8 <= len(password) <= 40:
        return False, "Password length must be between 8 and 20"
    return True, ""


def check_email(email):
    regex = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    if re.search(regex, email):
        return True
    return False


@ns.route('/')
class CreateUser(Resource):
    @api.expect(user_create_model, validate=True)
    def post(self):
        """
        Create new user
        :return: 200 or 400
        """
        b = request.get_json()
        username = b["username"]
        email = b["email"]

        valid, msg = check_username(username)
        if not valid:
            abort(400, msg)
        if not check_email(email):
            abort(400, "invalid email")

        user = User.objects(username=username).first()

        if user:
            abort(400, "User already exists")

        user = User.objects(email=email).first()

        if user:
            abort(400, "email has already been registered")

        password = b.get('password', '')
        valid, msg = check_password(password)
        if not valid:
            abort(400, msg)

        user = {
            "id": uuid.uuid4(),
            "email": email,
            "username": username,
            "password": encrypt_passwd(password),
        }

        user = User(**user)
        user.save()

        token = encode_user_token(user.get_id())
        res = OK('Logged in', {"token": token.decode("utf-8")})
        return res

    @token_required(type=['user'])
    @api.marshal_with(user_model, mask='username, email, role, active')
    def get(self):
        return g.token['user']


