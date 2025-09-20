from __future__ import annotations

import logging

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from service_locator import ServiceLocator
from service_locator import get_service_locator


logger = logging.getLogger(__name__)

entertainment_router = APIRouter()
templates = Jinja2Templates(directory="templates")
get_sl_dep = Depends(get_service_locator)


@entertainment_router.post("/api/entertainments", response_class=HTMLResponse)
async def create_entertainment(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_ent_contr().create_new_entertainment(request)
    logger.info("Развлечение успешно создано: %s", result)
    return templates.TemplateResponse("entertainment.html", {"request": request})


@entertainment_router.get("/entertainment.html", response_class=HTMLResponse)
async def get_all_entertainments(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    entertainment_list = await service_locator.get_ent_contr().get_all_entertainment()
    entertainments = entertainment_list.get("entertainments", []) 
    logger.info("Получено %d развлечений", len(entertainments))
    for e in entertainments:
        e['event_time'] = datetime.fromisoformat(e['event_time'])
    logger.info("Получение списка городов")
    cities_list = await service_locator.get_city_contr().get_all_cities()
    cities = cities_list.get("cities", [])
    logger.info("Получено %d городов", len(cities))
    return templates.TemplateResponse(
        "entertainment.html", 
        {
            "request": request, 
            "entertainments": entertainments, 
            "cities": cities
        }
    )


@entertainment_router.get("/entertainment/get/{entertainment_id}")
async def get_entertainment(entertainment_id: int, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        result = await service_locator.get_ent_contr().get_entertainment_details(entertainment_id)
        if result is None:
            logger.warning("Развлечение с ID %d не найдено", entertainment_id)
            raise HTTPException(status_code=404, detail="Entertainment not found")
        logger.info("Информация о развлечении получена: %s", result)
        return result
    except Exception as e:
        logger.error("Ошибка при получении информации о развлечении: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@entertainment_router.put("/api/entertainments/{entertainment_id}")
async def update_entertainment(entertainment_id: int, request: Request, 
                                service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_ent_contr().update_entertainment(entertainment_id, request)
    logger.info("Развлечение ID %d успешно обновлено: %s", entertainment_id, result)
    return templates.TemplateResponse("entertainment.html", {"request": request})


@entertainment_router.post("/entertainment/delete/{entertainment_id}", response_class=HTMLResponse)
async def delete_entertainment(entertainment_id: int, request: Request,
                                service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    result = await service_locator.get_ent_contr().delete_entertainment(entertainment_id)
    logger.info("Развлечение ID %d успешно удалено: %s", entertainment_id, result)
    return RedirectResponse(url="/entertainment.html", status_code=303)


@entertainment_router.delete("/route/entertainment/delete/{entertainment_id}", response_class=HTMLResponse)
async def delete_entertainment_for_route(entertainment_id: int, route_id: int,
                                service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    result = await service_locator.get_ent_contr().delete_entertainment(entertainment_id)
    logger.info("Развлечение ID %d успешно удалено: %s", entertainment_id, result)
    return RedirectResponse(url=f"/route/edit/{route_id}", status_code=303)


@entertainment_router.post("/entertainment/add/{route_id}", response_class=HTMLResponse)
async def add_ent_to_route(route_id: int, request: Request,
                                         service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    try:
        result = await service_locator.get_ent_contr().create_new_entertainment(request)
        logger.info("Развлечение успешно создано: %s", result)
        travel = await service_locator.get_travel_serv().get_travel_by_route_id(route_id)
        if not travel:
            raise ValueError(f"No travel found for route_id={route_id}")
        ent_ids = []
        entertainments = await service_locator.get_travel_serv().get_entertainments_by_travel(travel.travel_id)
        ent_ids = [e.entertainment_id for e in entertainments]
        ent_ids.append(result["entertainment_id"])

        await service_locator.get_travel_serv().link_entertainments(travel.travel_id, ent_ids)
        return RedirectResponse(
            url=f"/route/edit/{route_id}", 
            status_code=303
        )
        
    except Exception as e:
        logger.error(f"Error adding entertainment: {e!s}")
        raise


@entertainment_router.put("/entertainment/{entertainment_id}")
async def update_entertainment_dates(entertainment_id: int, request: Request,
    service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_ent_contr().update_entertainment_dates(entertainment_id, request)