import logging
import logging.config

CONFIG = '''
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "log_format": {
            "format": "%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(lineno)d in %(funcName)s] %(message)s"
        }
    },
    "filters": {
        "critical_shit": {
            "()" : "__main__.filter_maker",
            "level": "ERROR"
        }
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
             "level": "ERROR",
             "formatter": "log_format",
             "stream": "ext://sys.stderr",
             "filters": ["critical_shit"]
        }
    },
    "root": {
        "handlers": ["stderr"]
    }
}
'''


def filter_maker(level):
    level = getattr(logging, level)

    def filter(record):
        return record.levelno >= level

    return filter
