import hashlib

from collections.abc import Iterator
from tempfile import TemporaryDirectory

from fastapi import Request


async def get_temp_dir() -> Iterator[str]:
    dir = TemporaryDirectory()
    try:
        yield dir.name
    except Exception:
        raise
    finally:
        del dir


def client_hash(request: Request, behind_reverse_proxy: bool = False) -> str | None:
    """
    Returns the hashed value of either the last entry of the `X-Forwarded-For` header
    (if `behind_reverse_proxy` is `True`) or the client host – or `None` if neither
    of the above is present (for whatever reason).
    """
    ident = (
        str(request.headers.get("X-Forwarded-For", "")).split(",")[-1]
        if behind_reverse_proxy
        else request.client.host
    )
    if ident:
        return hashlib.sha256(ident.encode("utf-8")).hexdigest()
    else:  # pragma: no cover
        return None
