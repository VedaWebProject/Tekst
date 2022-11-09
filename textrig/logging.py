import logging
import os

from textrig.config import TextRigConfig, get_config


_cfg: TextRigConfig = get_config()


def _get_relevant_loggers() -> list[logging.Logger]:
    for logger in [
        "textrig",
        "fastapi",
        "uvicorn.access",
        "uvicorn.default",
        "uvicorn.error",
    ]:
        yield logging.getLogger(logger)


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

    else:

        """
        Colorful logging setup for development (app ran by uvicorn)
        """

        from colorlog import ColoredFormatter, StreamHandler

        # easy on the eye, no timestamps. perfect for development.
        dev_log_fmt = (
            "{bold}{log_color}{levelname:8}{reset} {white}{message}{blue} "
            "({name} - {process}:{threadName} - {filename}:{lineno})"
        )

        dev_log_formatter = ColoredFormatter(
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

        dev_log_handler = StreamHandler()
        dev_log_handler.setFormatter(dev_log_formatter)

        for logger in _get_relevant_loggers():
            for handler in logger.handlers:
                logger.removeHandler(handler)
            logger.addHandler(dev_log_handler)
            logger.setLevel(_cfg.log_level)


log = logging.getLogger("textrig")
