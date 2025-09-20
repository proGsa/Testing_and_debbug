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

accommodation_router = APIRouter()
templates = Jinja2Templates(directory="templates")
get_sl_dep = Depends(get_service_locator)


@accommodation_router.post("/api/accommodations", response_class=HTMLResponse)
async def create_accommodation(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_acc_contr().create_new_accommodation(request)
    logger.info("Проживание успешно создано: %s", result)
    return templates.TemplateResponse("accommodation.html", {"request": request})


@accommodation_router.get("/accommodation.html", response_class=HTMLResponse)
async def get_all_accommodations(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    accommodation_list = await service_locator.get_acc_contr().get_all_accommodation()
    accommodations = accommodation_list.get("accommodations", []) 
    logger.info("Получено %d проживаний", len(accommodations))
    for a in accommodations:
        a['check_in'] = datetime.fromisoformat(a['check_in'])
        a['check_out'] = datetime.fromisoformat(a['check_out'])
    logger.info("Получение списка городов")
    cities_list = await service_locator.get_city_contr().get_all_cities()
    cities = cities_list.get("cities", [])
    logger.info("Получено %d городов", len(cities))

    return templates.TemplateResponse(
        "accommodation.html",
        {
            "request": request, 
            "accommodations": accommodations, 
            "cities": cities
        }
    )


@accommodation_router.get("/accommodation/get/{accommodation_id}")
async def get_accommodation(accommodation_id: int, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    try:
        acc = await service_locator.get_acc_contr().get_accommodation_details(accommodation_id)
        if acc is None:
            logger.warning("Проживание с ID %d не найдено", accommodation_id)
            raise HTTPException(status_code=404, detail="Accommodation not found")
        logger.info("Информация о проживании ID %d получена", accommodation_id)
        return acc
    except Exception as e:
        logger.error("Ошибка при получении информации о проживании: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@accommodation_router.put("/api/accommodations/{accommodation_id}", response_class=HTMLResponse)
async def update_accommodation(accommodation_id: int, request: Request, 
                                service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_acc_contr().update_accommodation(accommodation_id, request)
    logger.info("Проживание ID %d успешно обновлено: %s", accommodation_id, result)
    return templates.TemplateResponse("accommodation.html", {"request": request})


@accommodation_router.post("/accommodation/delete/{accommodation_id}", response_class=HTMLResponse)
async def delete_accommodation(accommodation_id: int, service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    result = await service_locator.get_acc_contr().delete_accommodation(accommodation_id)
    logger.info("Проживание ID %d успешно удалено: %s", accommodation_id, result)
    return RedirectResponse(url="/accommodation.html", status_code=303)


@accommodation_router.delete("/route/accommodation/delete/{accommodation_id}", response_class=HTMLResponse)
async def delete_accommodation_for_route(accommodation_id: int, route_id: int,
                                service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    result = await service_locator.get_acc_contr().delete_accommodation(accommodation_id)
    logger.info("Размещение ID %d успешно удалено: %s", accommodation_id, result)
    return RedirectResponse(url=f"/route/edit/{route_id}", status_code=303)


@accommodation_router.post("/accommodation/add/{route_id}", response_class=HTMLResponse)
async def add_acc_to_route(route_id: int, request: Request,
                                         service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    try:
        result = await service_locator.get_acc_contr().create_new_accommodation(request)
        logger.info("Размещение успешно создано: %s", result)
        travel = await service_locator.get_travel_serv().get_travel_by_route_id(route_id)
        if not travel:
            raise ValueError(f"No travel found for route_id={route_id}")
        ent_ids = []
        accommodations = await service_locator.get_travel_serv().get_accommodations_by_travel(travel.travel_id)
        ent_ids = [e.accommodation_id for e in accommodations]
        ent_ids.append(result["accommodation_id"])

        await service_locator.get_travel_serv().link_accommodations(travel.travel_id, ent_ids)
        return RedirectResponse(
            url=f"/route/edit/{route_id}", 
            status_code=303
        )
        
    except Exception as e:
        logger.error(f"Error adding accommodation: {e!s}")
        raise


@accommodation_router.put("/accommodations/{accommodation_id}")
async def update_accommodation_dates(accommodation_id: int, request: Request,
    service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    return await service_locator.get_acc_contr().update_accommodation_dates(accommodation_id, request)