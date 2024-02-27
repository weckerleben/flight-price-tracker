import logging as log


def configure_log():
    log.basicConfig(filename='logs/prices.log', filemode='w', level=log.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
