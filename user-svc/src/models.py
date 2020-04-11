import datetime
from mongoengine import Document, fields


class User(Document):
    meta = {
        "indexes": [
            'email',
        ]
    }

    id = fields.UUIDField(primary_key=True, binary=False)
    username = fields.StringField(required=True, max_length=50)
    email = fields.EmailField(required=True, unique=True)
    password = fields.StringField(required=True)
    role = fields.StringField(default="user")
    active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow())
    modified_at = fields.DateTimeField(default=datetime.datetime.utcnow())

    def get_id(self):
        return self.id.__str__()

    def dict(self):
        return {
            'id': self.get_id(),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'active': self.active
        }