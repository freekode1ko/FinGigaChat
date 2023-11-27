import logging

log_format = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(lineno)d in %(funcName)s] %(message)s'
logging.basicConfig(filename="logs/main.log", filemode="a", format=log_format,
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger(__name__)
