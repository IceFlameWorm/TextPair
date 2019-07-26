import sys
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

class Logger(object):
    def __init__(self, app):
        logger_name = app.config['LOGGER_NAME']
        self.logging_level = app.config['LOGGING_LEVEL']
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(self.logging_level)
        self.logger.propagate = False

        log_file = app.config['ROTATING_LOG_FILE']
        max_bytes = app.config['ROTATING_MAX_BYTES']
        backup_count = app.config['ROTATING_BACKUP_COUNT']

        fmt = "%(asctime)-15s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s"
        datefmt = "%a %d %b %Y %H:%M:%S"
        formatter = logging.Formatter(fmt=fmt, datefmt= datefmt)

        self.file_handler = RotatingFileHandler(filename = log_file,
                                                maxBytes= max_bytes,
                                                backupCount= backup_count,
                                                encoding='utf-8'
                                               )
        self.file_handler.setLevel(self.logging_level)
        self.file_handler.setFormatter(formatter)

        self.stream_handler = StreamHandler()
        self.stream_handler.setLevel(logging.WARNING)
        self.stream_handler.setFormatter(formatter)

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stream_handler)


    def __getattr__(self, name):
        name2level = {'debug': self.logger.debug,
                      'info': self.logger.info,
                      'warning': self.logger.warning,
                      'error': self.logger.error,
                      'exception': self.logger.exception
                     }
        return name2level.get(name, self.logger.info)
            
    # def debug(self, msg, *args, **kwargs):
    #     self.logger.debug(msg, *args, **kwargs)

    # def info(self, msg, *args, **kwargs):
    #     self.logger.info(msg, *args, **kwargs)

    # def warning(self, msg, *args, **kwargs):
    #     self.logger.warning(msg, *args, **kwargs)

    # def error(self, msg, *args, **kwargs):
    #     self.logger.error(msg, *args, **kwargs)

    # def exception(self, msg, *args, **kwargs):
    #     self.logger.exception(msg, *args, **kwargs)

