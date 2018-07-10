from config import app, manager
from manage import user
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os


if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                   backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.DEBUG)
app.logger.info('Microblog startup')


if __name__ == '__main__':
    app.register_blueprint(blueprint=user)
    manager.run()

