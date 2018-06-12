import logging


def get_logger(name=''):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.indent = 0

    # create console handler and set level to debug
    ch = setup_handler(logger)

    # create formatter
    formatter = logging.Formatter('%(name)s - %(funcName)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return logger


def setup_handler(logger):
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            return handler
    logger.addHandler(handler)
    return handler
