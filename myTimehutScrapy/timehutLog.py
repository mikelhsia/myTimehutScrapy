import logging
import os

log_file_name = 'timehut.log'

if os.getenv("TIMEHUT_DEBUG") is not None:
    logging.basicConfig(filename=log_file_name,
                        format='%(asctime)s -%(name)s-%(levelname)s-%(module)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %p',
                        level=logging.DEBUG)
else:
    logging.basicConfig(filename=log_file_name,
                        format='%(asctime)s -%(name)s-%(levelname)s-%(module)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %p',
                        level=logging.INFO)

print(f"Module {__file__} is loaded...")
