from flask import request
from flask_restplus import fields, Resource

from . import api
from auth.token import encode_user_token
from models import User
from util import OK, check_password, abort

ns = api.namespace("Login",
                   path='/user/login',
                   description='Login endpoint')

login_model = api.model('LoginModel', {
    "email": fields.String(required=True),
    "password": fields.String(required=True)
})


@ns.route('/')
class Login(Resource):
    @api.expect(login_model, validate=True)
    def post(self):
        """
        return token if login succeed or return 404
        """
        b = request.get_json()

        user = User.objects(email=b["email"]).first()

        if not user or not check_password(user['password'], b['password']):
            abort(404, "Wrong username/password combination")

        token = encode_user_token(user.get_id())
        res = OK('Logged in', {"token": token.decode("utf-8")})

        return res
