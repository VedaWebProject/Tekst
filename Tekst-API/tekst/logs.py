import logging

from logging import config
from time import perf_counter, process_time
from typing import Literal
from uuid import uuid4

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


# label, start_t, level_code, use_process_time
_running_ops: dict[str, tuple[str, float, int, bool]] = dict()


def log_op_start(
    label: str,
    *,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG",
    use_process_time: bool = False,
) -> str:
    global _running_ops
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        level_code = logging.getLevelName("DEBUG")
    else:
        level_code = logging.getLevelName(level)
    op_id = str(uuid4())
    start_t = process_time() if use_process_time else perf_counter()
    _running_ops[op_id] = (label, start_t, level_code, use_process_time)
    log.log(level_code, f"Started: {label} ...")
    return op_id


def log_op_end(
    op_id: str,
    *,
    failed: bool = False,
    failed_msg: str | None = None,
    failed_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "ERROR",
    not_found_ok: bool = True,
) -> float:
    global _running_ops
    op_entry = _running_ops.pop(op_id, None)
    if op_entry is None:
        if not_found_ok:
            return 0
        else:
            raise RuntimeError(
                f"Operation {op_id} not found in running operations dict"
            )
    label, start_t, level_code, use_proc_t = op_entry
    dur = (process_time() if use_proc_t else perf_counter()) - start_t
    if not failed:
        log.log(level_code, f"Finished: {label} [took: {dur:.2f}s]")
    else:
        if failed_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            level_code = logging.getLevelName("ERROR")
        else:
            level_code = logging.getLevelName(failed_level)
        failed_msg = f" – {failed_msg}" if failed_msg else ""
        log.log(level_code, f"Failed: {label} [took: {dur:.2f}s]{failed_msg}")
    return dur
