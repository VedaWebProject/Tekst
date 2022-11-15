import importlib
import pkgutil
from types import FunctionType
from typing import Iterator

from fastapi import APIRouter


def get_routers() -> Iterator[APIRouter]:
    for mod in [mod.name.lower() for mod in pkgutil.iter_modules(__path__)]:
        module = importlib.import_module(f"{__name__}.{mod}")
        if hasattr(module, "get_router") and isinstance(
            module.get_router, FunctionType
        ):
            yield module.get_router()
