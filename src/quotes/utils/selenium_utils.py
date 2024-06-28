"""Позволяет подключаться к selenium."""

import logging
import time

from docker import errors as docker_errors
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from configs import config
from log.logger_base import Logger


def get_driver(logger: Logger.logger = None, connect_attempt_number: int = 1) -> WebDriver:
    """
    Получить подключение к селениуму.

    :param logger:                  Логгер
    :param connect_attempt_number:  Кол-во попыток подключения
    :return:                        подключение к селениум
    """
    logger = logger or logging.getLogger(__name__)

    logger.info(f'Подключение к контейнеру selenium, попытка №{connect_attempt_number}')
    try:
        time.sleep(5)
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument(f'--user-agent={config.user_agents[0]}')
        firefox_options.add_argument('start-maximized')
        firefox_options.add_argument('disable-infobars')
        firefox_options.add_argument('--disable-extensions')
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-application-cache')
        firefox_options.add_argument('--disable-gpu')
        firefox_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Remote(command_executor=config.SELENIUM_COMMAND_EXECUTOR, options=firefox_options)
    except docker_errors.DockerException as e:
        logger.error('При подключении к selenium произошла ошибка: %s', e)
        time.sleep(10)
        return get_driver(logger, connect_attempt_number + 1)

    return driver
