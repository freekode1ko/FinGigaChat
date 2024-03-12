# Позволяет запускать контейнер selenium
# В случае, если main_research запущен в контейнере,
# то у него должен быть прописан доступ к сервису docker
# для удаленного вызова команд
# ВАЖНО
# Для корректной работы скрипта должна быть настроена работа с Docker Engine
# https://docs.docker.com/engine/install/linux-postinstall/
# по умолчанию docker работает из-под sudo
# Если данный скрипт запускается не из-под sudo, то возникнет ошибка прав доступа

import logging
import time

import docker
from docker import errors as docker_errors
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from configs import config
from module.logger_base import Logger


def restart_container(logger: Logger.logger = None) -> None:
    """Перезапускает контейнер селениума с именем из конфига"""
    logger = logger or logging.getLogger(__name__)
    container_name = config.SELENIUM_CONTAINER_NAME
    client = docker.from_env()
    logger.info('Перезапуск контейнера selenium')

    try:
        container = client.containers.get(container_name)
    except docker_errors.NotFound:
        # Контейнер с таким именем не запускался, значит запустим его впервые
        run_container()
    except docker_errors.APIError as e:
        error_msg = f'Ошибка сервера при перезапуске контейнера с именем {container_name}: %s'
        print(error_msg % e)
        logger.error(error_msg, e)
    except Exception as e:
        error_msg = f'При перезапуске контейнера с именем {container_name} произошла ошибка: %s'
        print(error_msg % e)
        logger.error(error_msg, e)
    else:
        container.restart()


def stop_container(logger: Logger.logger = None) -> None:
    """Останавливает контейнер селениума с именем из конфига"""
    logger = logger or logging.getLogger(__name__)
    container_name = config.SELENIUM_CONTAINER_NAME
    client = docker.from_env()

    try:
        container = client.containers.get(container_name)
    except docker_errors.NotFound as e:
        error_msg = f'Контейнер с именем {container_name} не найден: %s'
        print(error_msg % e)
        logger.error(error_msg, e)
    except docker_errors.APIError as e:
        error_msg = f'Ошибка сервера при остановке контейнера с именем {container_name}: %s'
        print(error_msg % e)
        logger.error(error_msg, e)
    except Exception as e:
        error_msg = f'При остановке контейнера с именем {container_name} произошла ошибка: %s'
        print(error_msg % e)
        logger.error(error_msg, e)
    else:
        container.stop()


def run_container(logger: Logger.logger = None) -> None:
    """
    Запускает докер контейнер
    Эквивалентно
    docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" --name="selenium" selenium/standalone-firefox:latest
    """
    logger = logger or logging.getLogger(__name__)
    client = docker.from_env()

    try:
        client.containers.run(**config.SELENIUM_RUN_KWARGS)
        # docker.errors.ContainerError – If the container exits with a non-zero exit code and detach is False.
        # docker.errors.ImageNotFound – If the specified image does not exist.
        # docker.errors.APIError – If the server returns an error.
    except docker_errors.ImageNotFound as e:
        error_msg = f'Не удалось найти образ {config.SELENIUM_IMAGE_NAME}: %s'
        print(error_msg % e)
        logger.error(error_msg, e)
    except docker_errors.APIError as e:
        error_msg = f'Ошибка сервера при запуске контейнера с параметрами {config.SELENIUM_RUN_KWARGS}: %s'
        print(error_msg % e)
        logger.error(error_msg, e)
    except Exception as e:
        error_msg = f'При запуске контейнера с параметрами {config.SELENIUM_RUN_KWARGS} произошла ошибка: %s'
        print(error_msg % e)
        logger.error(error_msg, e)


def get_driver(logger: Logger.logger = None, connect_attempt_number: int = 1) -> WebDriver:
    """Подключается к селениуму и возвращает WebDriver"""
    logger = logger or logging.getLogger(__name__)

    logger.info(f'Подключение к контейнеру selenium, попытка №{connect_attempt_number}')
    try:
        # Сначала перезапускаем контейнер, потому что после ошибки при взаимодействии с selenium контейнер чаще падает,
        # чем остается в состоянии up
        restart_container(logger)
        # даем время на перезапуск
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
    except Exception as e:
        logger.error('При подключении к selenium произошла ошибка: %s', e)
        time.sleep(10)
        return get_driver(logger, connect_attempt_number + 1)

    return driver


# Есть два варианта проработки ошибок
# 1) Делаем везде, где работа с драйвером, try driver.work except driver = get_driver
#    Внутри get_driver при необходимости делаем restart_container
# 2) Завести для каждого метода драйвера отдельный обработчик и там выполнять переодплюкчение (менее понятный и более затратный)
