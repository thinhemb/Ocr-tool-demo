import logging
import os
import sys
import glob
from logging.handlers import TimedRotatingFileHandler

import dconfig


def _make_log_dir(path):
    try:
        os.umask(0)
        os.makedirs(path, mode=0o777, exist_ok=True)
        # os.makedirs(path)
    except Exception as e:
        print(e)
        pass


def _setup_log():
    log_dir = dconfig.config_object.LOG_DIR
    _make_log_dir(log_dir)
    logger = logging.getLogger('notiiime')
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(pathname)s:%(lineno)d | %(message)s')
    files = glob.glob(log_dir+'/*')
    for f in files:
        os.remove(f)
    path = '{}/info.log'.format(log_dir)
    file_handler = TimedRotatingFileHandler(path,
                                            when='midnight', backupCount=30)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    handler_console = logging.StreamHandler(stream=sys.stdout)
    handler_console.setFormatter(formatter)
    logger.addHandler(handler_console)
    logger.propagate = False
    if dconfig.config_object.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger


_logger = _setup_log()


def reset_logger():
    _logger.disabled = False


def dlog_e(error):
    _logger.error(error, exc_info=True)


def dlog_d(mess):
    _logger.debug(mess)


def dlog_i(info):
    _logger.info(info)
