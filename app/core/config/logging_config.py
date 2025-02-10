import logging
import os
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "access": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": "ext://sys.stdout",
        },
        "request_file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "/home/zaheer-ud-din/office-data/python-gen-ai-task/fast-api-blog-app-gen-ai/request.log",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False,
        },
        "request": {
            "level": "INFO",
            "handlers": ["request_file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["default"],
        "propagate": False,
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)