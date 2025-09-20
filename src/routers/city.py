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

city_router = APIRouter()
templates = Jinja2Templates(directory="templates")
get_sl_dep = Depends(get_service_locator)


@city_router.post("/api/cities", response_class=HTMLResponse)
async def create_city(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_city_contr().create_new_city(request)
    logger.info("Город успешно создан: %s", result)
    return templates.TemplateResponse("city.html", {"request": request})


@city_router.get("/city.html", response_class=HTMLResponse)
async def get_all_cities(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    city_list = await service_locator.get_city_contr().get_all_cities()
    cities = city_list.get("cities", [])
    logger.info("Получено %d городов", len(cities))
    return templates.TemplateResponse(
        "city.html",
        {
            "request": request,
            "cities": cities
        }
    )


@city_router.get("/city.html")
async def get_city(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_city_contr().get_city_details(request)
    if result is None:
        logger.warning("Город не найден")
        return {"error": "City not found"}
    logger.info("Информация о городе получена: %s", result)
    return result


@city_router.put("/api/cities/{city_id}", response_class=HTMLResponse)
async def update_city(city_id: int, request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_city_contr().update_city(city_id, request)
    logger.info("Город ID %d успешно обновлен: %s", city_id, result)
    return templates.TemplateResponse("city.html", {"request": request})


@city_router.post("/city/delete/{city_id}", response_class=HTMLResponse)
async def delete_city(city_id: int, service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    result = await service_locator.get_city_contr().delete_city(city_id)
    logger.info("Город ID %d успешно удален: %s", city_id, result)
    return RedirectResponse(url="/city.html", status_code=303)