import importlib
import pkgutil
from typing import Iterator

import humps
from fastapi import FastAPI
from fastapi.routing import APIRoute, APIRouter
from textrig.logging import log


def _get_routers() -> Iterator[APIRouter]:
    for mod in [mod.name.lower() for mod in pkgutil.iter_modules(__path__)]:
        module = importlib.import_module(f"{__name__}.{mod}")
        if hasattr(module, "router") and isinstance(module.router, APIRouter):
            yield module.router


def setup_routes(app: "FastAPI") -> None:
    """
    Connects the API routers defined in this module to the passed application instance.
    Also, generates operation IDs based on endpoint function names for each route
    and configures the route to use these names.
    They will then be used in the generated OpenAPI schema.

    :param app: FastAPI app instance
    :type app: FastAPI
    """
    log.info("Setting up API routes")
    for router in _get_routers():
        rc = len(router.routes)
        log.debug(f"\u2022 {router.prefix}/... ({rc} route{'s' if rc != 1 else ''})")
        for route in router.routes:
            if isinstance(route, APIRoute):
                route.operation_id = humps.camelize(route.name)
        app.include_router(router)
