# v0.2
# 

import logging
import os



def set_logger(name, new_file_on_run: bool = True, log_folder='logs', log_file_name='info.log'):
    SELF_LOGGER = logging.getLogger(__name__)
    self_formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    )
    self_file_info_handler = logging.FileHandler(f'{log_folder}/.{__name__}.log')
    self_file_info_handler.setFormatter(self_formatter)
    SELF_LOGGER.addHandler(self_file_info_handler)
    SELF_LOGGER.setLevel(logging.INFO)
    SELF_LOGGER.info('     ***** NEW RUN *****     ')


    logger = logging.getLogger(name)
    log_level = logging.INFO
    logger.setLevel(log_level)
    SELF_LOGGER.info(f'set_logger: {logger.name} {logger} created')
    
    formatter_text = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'

    formatter = logging.Formatter(formatter_text)
    SELF_LOGGER.info(f'set_logger: formatter created: {formatter_text}')
    
    log_file = f'{log_folder}/{log_file_name}'
    if os.path.exists(log_file) and new_file_on_run:
        os.remove(log_file)
    file_info_handler = logging.FileHandler(f'{log_folder}/{log_file_name}',)
    file_info_handler.setFormatter(formatter)
    file_info_handler.setLevel(logging.INFO)

    logger.addHandler(file_info_handler)
    SELF_LOGGER.info(f'set_logger: {file_info_handler} added to logger')
    logger.info('          **********   NEW RUN   **********          ')

    return logger

def test():
    logger = set_logger(__name__)
    print(logger)
    logger.info('test')
    
if __name__ == '__main__':
    test()
