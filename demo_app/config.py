import os
import logging

FILE_PATH = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(FILE_PATH, '..')
LOGS_PATH = os.path.join(FILE_PATH, 'logs')

if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)


class Config(object):
    DEBUG = True
    
    LOGGER_NAME = 'TextPairApp'
    ROTATING_LOG_FILE = os.path.join(LOGS_PATH, 'app.log')
    ROTATING_MAX_BYTES = 2e6 # 2M
    ROTATING_BACKUP_COUNT = 5

    if DEBUG:
        LOGGING_LEVEL = logging.DEBUG
    else:
        LOGGING_LEVEL = logging.INFO
