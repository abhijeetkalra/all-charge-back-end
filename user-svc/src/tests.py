import unittest

from app import app, init
from auth.token import decode_token, encode_user_token
from db import init_db
from models import User


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        init(app)
        init_db(app)
        self.cli = app.test_client()
        self.admin_token = encode_user_token(app.config['ADMIN_USERNAME']).decode("utf-8")
        normal_user = {
            "username": "normal",
            "password": "normalpassword"
        }
        User.objects(username=normal_user["username"]).upsert_one(**normal_user).save()
        self.user_token = encode_user_token("normal").decode("utf-8")

    def get_headers(self, token):
        headers = {
            "Authorization": "token " + token
        }
        return headers

    def test_login(self):
        res = self.cli.post("/api/v1/login", json={
            "username": app.config['ADMIN_USERNAME'],
            "password": app.config['ADMIN_PASSWORD']
        })
        self.assertEqual(res.status_code, 200)
        token = res.json['token']
        self.assertEqual(decode_token(token)['user']['username'], app.config['ADMIN_USERNAME'])

    def test_wrong_login(self):
        res = self.cli.post("/api/v1/login", json={
            "username": "fakeuser",
            "password": "fakepassword"
        })
        self.assertEqual(res.status_code, 404)

    def test_create_user(self):
        user = {
            "username": "test1",
            "password": "test1password",
            "role": "user",
            "active": True
        }
        res = self.cli.post("/api/v1/user",
                            json=user)
        # no token
        self.assertEqual(res.status_code, 401)

        # check permission
        res = self.cli.post("/api/v1/user",
                            headers=self.get_headers(self.user_token),
                            json=user)
        self.assertEqual(res.status_code, 403)

        res = self.cli.post("/api/v1/user",
                            headers=self.get_headers(self.admin_token),
                            json=user)
        self.assertEqual(res.status_code, 200)

        res = self.cli.post("/api/v1/user",
                            headers=self.get_headers(self.admin_token),
                            json=user)
        # User already exists
        self.assertEqual(res.status_code, 400)

        user['username'] = "@123"
        res = self.cli.post("/api/v1/user",
                            headers=self.get_headers(self.admin_token),
                            json=user)
        # invalid username
        self.assertEqual(res.status_code, 400)

        user['username'] = "test2"
        user['password'] = "short"
        res = self.cli.post("/api/v1/user",
                            headers=self.get_headers(self.admin_token),
                            json=user)
        # password too short
        self.assertEqual(res.status_code, 400)

    def test_get_user(self):
        res = self.cli.get("/api/v1/user/nouser")
        # no token
        self.assertEqual(res.status_code, 401)

        res = self.cli.get("/api/v1/user/nouser",
                           headers=self.get_headers(self.admin_token))
        # not exist
        self.assertEqual(res.status_code, 404)

        res = self.cli.get("/api/v1/user/normal",
                           headers=self.get_headers(self.user_token))
        # check permission
        self.assertEqual(res.status_code, 403)

        res = self.cli.get("/api/v1/user/" + app.config['ADMIN_USERNAME'],
                           headers=self.get_headers(self.admin_token))

        self.assertEqual(res.status_code, 200)

    def test_modify_user(self):
        user = {
            "active": False,
            "role": "user",
            "password": "newpassword"
        }
        res = self.cli.put("/api/v1/user/nouser", json=user)
        # no token
        self.assertEqual(res.status_code, 401)

        res = self.cli.get("/api/v1/user/nouser", json=user,
                           headers=self.get_headers(self.admin_token))
        # not exist
        self.assertEqual(res.status_code, 404)

        res = self.cli.put("/api/v1/user/normal", json=user,
                           headers=self.get_headers(self.user_token))
        # check permission
        self.assertEqual(res.status_code, 403)

        res = self.cli.put("/api/v1/user/normal", json=user,
                           headers=self.get_headers(self.admin_token))

        self.assertEqual(res.status_code, 200)

        res = self.cli.get("/api/v1/user/normal",
                           headers=self.get_headers(self.admin_token))
        self.assertEqual(res.json['active'], False)

    def test_delete_user(self):
        user = {
            "username": "todelete",
            "password": "password1",
            "role": "user",
            "active": True
        }

        res = self.cli.post("/api/v1/user",
                            headers=self.get_headers(self.admin_token),
                            json=user)
        self.assertEqual(res.status_code, 200)

        res = self.cli.delete("/api/v1/user/nouser")
        # no token
        self.assertEqual(res.status_code, 401)

        res = self.cli.delete("/api/v1/user/nouser",
                              headers=self.get_headers(self.admin_token))
        # not exist
        self.assertEqual(res.status_code, 404)

        res = self.cli.delete("/api/v1/user/todelete",
                              headers=self.get_headers(self.user_token))
        # check permission
        self.assertEqual(res.status_code, 403)

        res = self.cli.delete("/api/v1/user/todelete",
                              headers=self.get_headers(self.admin_token))

        self.assertEqual(res.status_code, 200)


if __name__ == '__main__':
    unittest.main()
