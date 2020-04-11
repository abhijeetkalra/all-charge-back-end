

def init_db(app):
    """
    Init db, create admin user
    :app: Flask instance
    :return: None
    """
    return
    # app.logger.info("initing db")
    #
    # admin_user = {
    #     "username": app.config['ADMIN_USERNAME'],
    #     "password": encrypt_passwd(app.config['ADMIN_PASSWORD']),
    #     "role": "admin",
    #     "active": True
    # }
    #
    # User.objects(username=admin_user["username"]).upsert_one(**admin_user).save()
    # app.logger.info("initing db finished")
