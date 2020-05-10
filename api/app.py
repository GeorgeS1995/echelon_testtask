import sys
from flask import Flask
from .route import bp
from logging.config import dictConfig
import datetime
import os
from .exception import PythonVersionError

if sys.version_info.major < 3 or sys.version_info.minor < 7 or sys.version_info.micro < 2:
    raise PythonVersionError(sys.version.split(" ")[0])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = 'logs'
now = datetime.datetime.now()
format_time = now.strftime("%Y%m%d%H%M%S")

if os.environ.get('FLASK_TEST'):
    from .configuration import ConfigurationTest as Configuration
else:
    from .configuration import Configuration

if not Configuration.LOG_DIR:
    Configuration.LOG_DIR = os.path.join(BASE_DIR, LOG_DIR)

if not os.path.exists(os.path.join(BASE_DIR, Configuration.LOG_DIR)):
    os.makedirs(os.path.join(BASE_DIR, Configuration.LOG_DIR))

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, Configuration.LOG_DIR, f"{format_time}.log"),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': Configuration.LOG_LEVEL,
        'handlers': ['file', 'console'],
    }
})

app = Flask(__name__)

if not Configuration.DB_FILE_PATH:
    Configuration.DB_FILE_PATH = os.path.join(BASE_DIR, 'db.json')
else:
    Configuration.DB_FILE_PATH = os.path.join(BASE_DIR, Configuration.DB_FILE_PATH)
    db_ext = os.path.splitext(Configuration.DB_FILE_PATH)
    if db_ext[1] != '.json':
        msg = f'wrong db file extention: {db_ext[1]}'
        app.logger.error(msg)
        raise Exception(msg)

if not os.path.exists(Configuration.DB_FILE_PATH):
    try:
        open(os.path.abspath(Configuration.DB_FILE_PATH), 'a').close()
    except OSError as err:
        msg = f"Can't create db file: {err}"
        app.logger.error(msg)
        raise Exception(msg)

app.config.from_object(Configuration)
app.register_blueprint(bp)