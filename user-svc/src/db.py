import uuid
from models import User
from util import encrypt_passwd


def init_db(app):
    """
    Init db, create admin user
    :app: Flask instance
    :return: None
    """
    app.logger.info("initing db")

    admin_user = {
        "id": '00000000-0000-0000-0000-000000000000',
        "username": app.config['ADMIN_USERNAME'],
        "email": app.config['ADMIN_EMAIL'],
        "password": encrypt_passwd(app.config['ADMIN_PASSWORD']),
        "role": "admin",
        "active": True
    }
    user = User.objects(id=admin_user['id']).first()
    if user:
        del admin_user['id']
        user.update(**admin_user)
        user.save()
    else:
        User(**admin_user).save()
    app.logger.info("initing db finished")
