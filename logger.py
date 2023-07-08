import logging


def main():
    # test logger
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
            filename='test.log',
            filemode='a',
        )


    # create the info logger
    info_logger = logging.getLogger('BOT INFO')
    info_logger.setLevel(logging.INFO)

    info_handler = logging.FileHandler('info.log')
    info_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    info_handler.setFormatter(formatter)

    info_logger.addHandler(info_handler)


    # create the error logger
    error_logger = logging.getLogger('BOT ERROR')
    error_logger.setLevel(logging.ERROR)

    error_handler = logging.FileHandler('error.log')
    error_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter('!%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    error_handler.setFormatter(formatter)

    error_logger.addHandler(error_handler)


    # create the debug logger
    debug_logger = logging.getLogger('BOT DEBUG')
    debug_logger.setLevel(logging.DEBUG)

    debug_handler = logging.FileHandler('debug.log')
    debug_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    debug_handler.setFormatter(formatter)

    debug_logger.addHandler(debug_handler)