import hashlib
import inspect

from tempfile import TemporaryDirectory
from types import AsyncGeneratorType
from typing import Any, cast

from fastapi import Request


async def get_temp_dir() -> AsyncGeneratorType[str]:
    dir = TemporaryDirectory()
    try:
        yield dir.name
    except Exception:
        raise
    finally:
        del dir


def client_hash(
    request: Request,
    behind_reverse_proxy: bool = False,
) -> str | None:
    """
    Returns the hashed value of either the last entry of the `X-Forwarded-For` header
    (if `behind_reverse_proxy` is `True`) or the client host – or `None` if neither
    of the above is present (for whatever reason).
    """
    ident = (
        str(request.headers.get("X-Forwarded-For", "")).split(",")[-1]
        if behind_reverse_proxy
        else request.client.host
        if request.client
        else None
    )
    if ident:
        return hashlib.sha256(ident.encode("utf-8")).hexdigest()
    else:  # pragma: no cover
        return None


def ensure[T](
    v: T | None | Any,
    *,
    strict: bool = False,
) -> T:
    """
    Raises a ValueError if `v` is None (default) or falsy (set via `strict`).
    Uses typing.cast to make extra sure type checkers understand that the returned
    value is of the desired type.
    """
    if v is None or (strict and not v):
        frame_info = inspect.stack()[1]
        module = inspect.getmodule(frame_info.frame)
        module_repr = module.__file__ if module else frame_info.filename
        v_str = "<empty_str>" if isinstance(v, str) else str(v)
        raise ValueError(
            f"Unexpected {v_str} value at: "
            f"{module_repr}, {frame_info.function}, line {frame_info.lineno}"
        )
    return cast(T, v)
