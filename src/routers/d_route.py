from __future__ import annotations

import logging

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from service_locator import ServiceLocator
from service_locator import get_service_locator


logger = logging.getLogger(__name__)

d_router = APIRouter()
templates = Jinja2Templates(directory="templates")
get_sl_dep = Depends(get_service_locator)


@d_router.post("/api/directory_routes", response_class=HTMLResponse)
async def create_d_route(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_d_route_contr().create_new_d_route(request)
    logger.info("Справочный маршрут успешно создан: %s", result)
    return templates.TemplateResponse("directory_route.html", {"request": request})


@d_router.get("/directory_route.html", response_class=HTMLResponse)
async def get_all_d_routes(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    d_route_list = await service_locator.get_d_route_contr().get_all_d_routes()
    d_routes = d_route_list.get("d_routes", [])
    logger.info("Получено %d справочных маршрутов", len(d_routes))
    
    logger.info("Получение списка городов")
    cities_list = await service_locator.get_city_contr().get_all_cities()
    cities = cities_list.get("cities", [])
    logger.info("Получено %d городов", len(cities))
    
    return templates.TemplateResponse(
        "directory_route.html",
        {
            "request": request,
            "d_routes": d_routes,
            "cities": cities
        }
    )


@d_router.get("/directory_route.html")
async def get_d_route(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_d_route_contr().get_d_route_details(request)
    if result is None:
        logger.warning("Справочный маршрут не найден")
        return {"error": "Directory route not found"}
    logger.info("Информация о справочном маршруте получена: %s", result)
    return result


@d_router.put("/api/directory_routes/{d_route_id}", response_class=HTMLResponse)
async def update_d_route(d_route_id: int, request: Request, 
                                            service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_d_route_contr().update_d_route(d_route_id, request)
    logger.info("Справочный маршрут ID %d успешно обновлен: %s", d_route_id, result)
    return templates.TemplateResponse("directory_route.html", {"request": request})


@d_router.post("/directory_route/delete/{d_route_id}", response_class=HTMLResponse)
async def delete_d_route(d_route_id: int, service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    result = await service_locator.get_d_route_contr().delete_d_route(d_route_id)
    logger.info("Справочный маршрут ID %d успешно удален: %s", d_route_id, result)
    return RedirectResponse(url="/directory_route.html", status_code=303)