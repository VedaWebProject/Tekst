import logging

from logging import config

from tekst.config import TekstConfig, get_config


_cfg: TekstConfig = get_config()

_FMT_DEFAULT = "%(asctime)s - %(levelprefix)s %(message)s"
_FMT_DEFAULT_DEV = (
    "%(levelprefix)s %(message)s (%(funcName)s @ %(filename)s:%(lineno)d)"
)
_FMT_ACCESS = (
    "%(asctime)s - %(levelprefix)s %(client_addr)s"
    ' - "%(request_line)s" %(status_code)s'
)
_FMT_ACCESS_DEV = "%(levelprefix)s %(request_line)s - %(status_code)s"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": _FMT_DEFAULT if not _cfg.dev_mode else _FMT_DEFAULT_DEV,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": _FMT_ACCESS if not _cfg.dev_mode else _FMT_ACCESS_DEV,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "tekst": {
            "handlers": ["default"],
            "level": _cfg.log_level,
            "propagate": False,
        },
        "fastapi": {
            "handlers": ["default"],
            "level": _cfg.log_level,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["default"],
            "level": _cfg.log_level,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": _cfg.log_level,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": _cfg.log_level,
            "propagate": False,
        },
        "gunicorn.error": {
            "handlers": ["default"],
            "level": _cfg.log_level,
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["access"],
            "level": _cfg.log_level,
            "propagate": False,
        },
    },
}

config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger("tekst")
