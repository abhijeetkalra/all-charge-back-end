import os
import sys
if os.environ.get('FLASK_ENV') == "production":
    import eventlet
    eventlet.monkey_patch()
    from eventlet import wsgi
from app import app, init
from db import init_db
from util import get_logger

logger = get_logger('user')
app.logger = logger

init(app)
init_db(app)

if __name__ == '__main__':
    app.logger.info("Starting server")
    if os.environ.get('FLASK_ENV') == "production":
        wsgi.server(eventlet.listen(('0.0.0.0', app.config['PORT'])), app, debug=False, log_output=False)
    else:
        app.run(port=app.config['PORT'])
