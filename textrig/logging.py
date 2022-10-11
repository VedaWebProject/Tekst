import logging
import os

from textrig.config import TextRigConfig, get_config


_cfg: TextRigConfig = get_config()


def _get_relevant_loggers() -> list[logging.Logger]:

    loggers = [
        "textrig",
        "fastapi",
        "uvicorn.access",
        "uvicorn.default",
        "uvicorn.error",
    ]

    return [logging.getLogger(logger) for logger in loggers]


def setup_logging() -> None:

    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):

        """
        This should trigger in production running gunicorn with uvicorn workers,
        funneling all the logs into the gunicorn log handlers...
        """

        # if running with gunicorn, we're letting gunicorn handle all logging
        gunicorn_logger = logging.getLogger("gunicorn.error")
        gunicorn_logger.setLevel(_cfg.log_level)

        # Use gunicorn error handlers for textrig-, uvicorn-, and fastapi loggers;
        # Pass on logging levels for textrig-, uvicorn-, and fastapi loggers
        for logger in _get_relevant_loggers():
            logger.handlers = gunicorn_logger.handlers
            logger.setLevel(_cfg.log_level)

    elif _cfg.dev_mode:

        """
        Colorful logging setup for development (app ran by uvicorn)
        """

        from colorlog import ColoredFormatter, StreamHandler

        # easy on the eye, no timestamps. perfect for development.
        dev_log_fmt = (
            "{bold}{log_color}{levelname:8}{reset} {white}{message}{blue} "
            "({name} - {process}:{threadName} - {filename}:{lineno})"
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

        for logger in _get_relevant_loggers():
            logger.addHandler(handler)
            logger.setLevel(_cfg.log_level)

    else:

        """
        A possible case: Production use without gunicorn (e.g. in a cluster).
        Not planned, just a placeholder...
        """

        pass


log = logging.getLogger("textrig")
