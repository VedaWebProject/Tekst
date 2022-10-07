import logging
import os

from fastapi.logger import logger as fastapi_logger
from textrig.config import TextRigConfig, get_config


_cfg: TextRigConfig = get_config()


def setup_logging() -> None:

    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):

        """
        This should trigger in production running gunicorn with uvicorn workers,
        funneling all the logs into the gunicorn log handlers...
        """

        # collect loggers
        root_logger = logging.getLogger()
        gunicorn_logger = logging.getLogger("gunicorn.error")
        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        uvicorn_default_logger = logging.getLogger("uvicorn.default")

        # Use gunicorn error handlers for root, uvicorn, and fastapi loggers
        root_logger.handlers = gunicorn_logger.handlers
        uvicorn_access_logger.handlers = gunicorn_logger.handlers
        uvicorn_default_logger.handlers = gunicorn_logger.handlers
        fastapi_logger.handlers = gunicorn_logger.handlers

        # Pass on logging levels for root, uvicorn, and fastapi loggers
        root_logger.setLevel(_cfg.log_level)
        gunicorn_logger.setLevel(_cfg.log_level)
        uvicorn_access_logger.setLevel(_cfg.log_level)
        uvicorn_default_logger.setLevel(_cfg.log_level)
        fastapi_logger.setLevel(_cfg.log_level)

    elif _cfg.dev_mode:

        """
        Colorful logging setup for development (app ran by uvicorn)
        """

        from colorlog import ColoredFormatter, StreamHandler

        dev_log_fmt = (
            "{bold}{log_color}{levelname:8}{reset} {white}{message}{blue} "
            "\u2022 {name} \u2022 {process}:{threadName} \u2022 {filename}:{lineno}"
        )

        formatter = ColoredFormatter(
            dev_log_fmt,
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="{",
        )

        handler = StreamHandler()
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(_cfg.log_level)

    else:

        """
        A possible case: Production use without gunicorn (e.g. in a cluster).
        Not planned, just a placeholder...
        """

        pass


log = logging.getLogger("textrig")
