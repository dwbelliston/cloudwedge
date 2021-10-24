'''
Logger

Used by other modules to get a common logger
'''

import logging


def get_logger(name, log_level=None):
    '''Logger with formatting and such'''

    log_level = log_level if log_level else logging.INFO

    # create logger
    logger = logging.getLogger(name)

    if len(logger.handlers) == 0:
        logger.setLevel(log_level)

        # create console handler and set level to debug
        streamhandle = logging.StreamHandler()
        streamhandle.setLevel(log_level)

        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to streamhandle
        streamhandle.setFormatter(formatter)

        # add streamhandle to logger
        logger.addHandler(streamhandle)

        # dont double log to root logger
        logger.propagate = False

    return logger
