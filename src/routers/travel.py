from __future__ import annotations

import logging

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from service_locator import ServiceLocator
from service_locator import get_service_locator


logger = logging.getLogger(__name__)

travel_router = APIRouter()
templates = Jinja2Templates(directory="templates")
get_sl_dep = Depends(get_service_locator)


@travel_router.post("/api/travels", response_class=HTMLResponse)
async def create_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_travel_contr().create_new_travel(request)
    logger.info("Путешествие успешно создано: %s", result)
    return templates.TemplateResponse("travel.html", {"request": request})


@travel_router.get("/travel.html", response_class=HTMLResponse)
async def get_all_travels(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    travel_list = await service_locator.get_travel_contr().get_all_travels()
    travels = travel_list.get("travels", [])
    logger.info("Получено %d путешествий", len(travels))
    
    user_id = travels[0]["user_id"] if travels else None
    user = None
    if user_id is not None:
        logger.info("Получение данных пользователя ID %s", user_id)
        user = await service_locator.get_user_contr().get_user_profile(user_id)
    users = await service_locator.get_user_contr().get_all_users()
    all_entertainments = await service_locator.get_ent_contr().get_all_entertainment()
    all_accommodations = await service_locator.get_acc_contr().get_all_accommodation()

    entertainments = travel_list.get("entertainments", [])
    for e in all_entertainments["entertainments"]:
        e['event_time'] = datetime.fromisoformat(e['event_time'])
    for e in entertainments:
        e['event_time'] = datetime.fromisoformat(e['event_time'])
    accommodations = travel_list.get("accommodations", [])
    for a in accommodations:
        a['check_in'] = datetime.fromisoformat(a['check_in'])
        a['check_out'] = datetime.fromisoformat(a['check_out'])
    for a in all_accommodations["accommodations"]:
        a['check_in'] = datetime.fromisoformat(a['check_in'])
        a['check_out'] = datetime.fromisoformat(a['check_out'])

    for travel in travels:
        for entertainment in travel["entertainments"]:
            if isinstance(entertainment.get("city"), dict):
                entertainment["city_name"] = entertainment["city"].get("name", "Undefined")
            elif hasattr(entertainment.get("city"), "name"): 
                entertainment["city_name"] = entertainment["city"].name
            else:
                entertainment["city_name"] = "Undefined"

        # Для размещений
        for accommodation in travel["accommodations"]:
            if isinstance(accommodation.get("city"), dict):
                accommodation["city_name"] = accommodation["city"].get("name", "Undefined")
            elif hasattr(accommodation.get("city"), "name"):  # Если это объект модели
                accommodation["city_name"] = accommodation["city"].name
            else:
                accommodation["city_name"] = "Undefined"

    logger.info("Данные о развлечениях и проживании обработаны")
    return templates.TemplateResponse(
        "travel.html",
        {
            "request": request, 
            "travels": jsonable_encoder(travels),
            "user": user['user'] if user else None,
            "entertainments": entertainments,
            "accommodations": accommodations,
            "users": users["users"],
            "all_entertainments": all_entertainments["entertainments"],
            "all_accommodations": all_accommodations["accommodations"]
        },
    )


@travel_router.put("/api/travels/{travel_id}", response_class=HTMLResponse)
async def update_travel(travel_id: int, request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_travel_contr().update_travel(travel_id, request)
    logger.info("Путешествие ID %d успешно обновлено: %s", travel_id, result)
    return templates.TemplateResponse("travel.html", {"request": request})


@travel_router.post("/travel/delete/{travel_id}", response_class=HTMLResponse)
async def delete_travel(travel_id: int, request: Request, 
                                            service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    result = await service_locator.get_travel_contr().delete_travel(travel_id)
    logger.info("Путешествие ID %d успешно удалено: %s", travel_id, result)
    return RedirectResponse(url="/travel.html", status_code=303)


@travel_router.post("/travel/complete/{travel_id}")
async def complete_travel(travel_id: int, request: Request, 
                                                service_locator: ServiceLocator = get_sl_dep) -> Response:
    result = await service_locator.get_travel_contr().complete_travel(travel_id)
    logger.info("Путешествие успешно завершено: %s", result)
    travel = await service_locator.get_travel_contr().get_travel_details(travel_id)
    user_id = travel['travel'].get("user_id")
    if not user_id:
        logger.error("Не удалось получить user_id для путешествия ID %d", travel_id)
        return HTMLResponse(content="<h1>Пользователь не найден</h1>", status_code=404)
    return RedirectResponse(url=f"/profile_user/{user_id}", status_code=303)


@travel_router.post("/search")
async def search_travel(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_travel_contr().search_travel(request)
    logger.info("Поиск завершен, найдено %d путешествий", len(result.get("travels", [])))
    return result
