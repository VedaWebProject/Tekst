import importlib
import pkgutil

from typing import Iterator

import humps

from fastapi import FastAPI
from fastapi.routing import APIRoute, APIRouter

from tekst.auth import setup_auth_routes
from tekst.logging import log


def _get_routers() -> Iterator[APIRouter]:
    for mod in [mod.name.lower() for mod in pkgutil.iter_modules(__path__)]:
        module = importlib.import_module(f"{__name__}.{mod}")
        if hasattr(module, "router") and isinstance(module.router, APIRouter):
            yield module.router


def setup_routes(app: FastAPI) -> None:
    """
    Connects the API routers defined in this module to the passed application instance.
    Also, generates operation IDs based on endpoint function names for each route
    and configures the route to use these names.
    They will then be used in the generated OpenAPI schema.

    :param app: FastAPI app instance
    :type app: FastAPI
    """
    log.info("Setting up API routes")
    # register routers that aren't auth-related
    for router in _get_routers():
        app.include_router(router)
    # register auth-related routers
    setup_auth_routes(app)
    # modify routes...
    for route in app.routes:
        if isinstance(route, APIRoute):
            # generate route operation IDs from route names
            route.operation_id = humps.camelize(route.name)
            route_name = getattr(route.endpoint, "__name__", route.name)
            route.summary = route_name.replace("_", " ").capitalize()
            # add camel-cased aliases to route params
            for param in route.dependant.query_params:
                if not param.field_info.alias:
                    param.alias = humps.camelize(param.name)
            for param in route.dependant.path_params:
                if not param.field_info.alias:
                    param.alias = humps.camelize(param.name)
