"""Проводит сбор ответов на тестовом датасете. """
import sys

import asyncio

from config_evaluation import LOG_FILE, LOG_LEVEL
from evaluation_utils import get_answers
from log.logger_base import selector_logger

sys.path.append('../')
from retriever import Chain

logger = selector_logger(LOG_FILE, LOG_LEVEL)
engine = Chain(logger)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_answers(engine, logger))
    return


if __name__ == '__main__':
    main()
