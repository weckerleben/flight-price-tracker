import logging


def configure_logging():
    logging.basicConfig(filename='prices.log', filemode='w', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
