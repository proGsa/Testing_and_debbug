from __future__ import annotations

import logging

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from service_locator import ServiceLocator
from service_locator import get_service_locator


logger = logging.getLogger(__name__)

user_router = APIRouter()

templates = Jinja2Templates(directory="templates")

get_sl_dep = Depends(get_service_locator)


@user_router.post("/api/register")
async def register_user(request: Request, service_locator: ServiceLocator = get_sl_dep) -> JSONResponse:
    result = await service_locator.get_user_contr().registrate(request)
    logger.info("Пользователь успешно зарегистрирован: %s", result)
    
    return JSONResponse({
        "access_token": result["access_token"],
        "user_id": result["user_id"],
        "message": "Регистрация прошла успешно"
    })


@user_router.get("/profile")
async def show_profile(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("profile.html", {"request": request})


@user_router.post("/api/users", response_class=HTMLResponse)
async def register_admin(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_user_contr().create_admin(request)
    logger.info("Администратор успешно зарегистрирован: %s", result)
    return templates.TemplateResponse("user.html", {"request": request})


@user_router.put("/api/users/{user_id}", response_class=HTMLResponse)
async def update_admin(user_id: int, request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    result = await service_locator.get_user_contr().update_admin(user_id, request)
    logger.info("Администратор успешно обновлен: %s", result)
    return templates.TemplateResponse("user.html", {"request": request})


@user_router.post("/api/login")
async def login_user(request: Request, service_locator: ServiceLocator = get_sl_dep) -> dict[str, Any]:
    result = await service_locator.get_user_contr().login(request)
    logger.info("Результат входа: %s", result)
    return result


@user_router.get("/profile_user/{user_id}", response_class=HTMLResponse)
async def get_user_profile(user_id: int, request: Request, 
                                        service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    profile_data = await service_locator.get_user_contr().get_user_profile(user_id)
    active_routes = await service_locator.get_route_serv().get_routes_by_user_and_status_and_type(user_id, 
                                                                                            "В процессе", 'Свои')
    completed_routes = await service_locator.get_route_serv().get_routes_by_user_and_status_and_type(user_id, 
                                                                                                'Завершен', 'Свои')
    logger.info("completed_routes %s", completed_routes)
    routes_active_data = []
    for route in active_routes:
        transport_cost = route.d_route.cost if route.d_route else 0
        accommodations = route.travels.accommodations if route.travels else []
        accommodation_cost = sum(acc.price for acc in accommodations)
        total_cost = transport_cost + accommodation_cost

        users = []
        if route.travels and route.travels.travel_id:
            users_raw = await service_locator.get_travel_serv().get_users_by_travel(route.travels.travel_id)
            users = [user for user in users_raw if user is not None]

        route_dict = {
            "route_id": route.route_id,
            "start_time": route.start_time,
            "end_time": route.end_time,
            "transport": route.d_route.type_transport if route.d_route else None,
            "cost": total_cost,
            "destination_city": route.d_route.destination_city.name if route.d_route 
                                                and route.d_route.destination_city else None,
            "entertainments": route.travels.entertainments if route.travels else [],
            "accommodations": route.travels.accommodations if route.travels else [],
            "travel_id": route.travels.travel_id if route.travels else None,
            "users": users

        }
        routes_active_data.append(route_dict)

    routes_completed_data = []
    for route in completed_routes:
        transport_cost = route.d_route.cost if route.d_route else 0
        accommodations = route.travels.accommodations if route.travels else []
        accommodation_cost = sum(acc.price for acc in accommodations)
        total_cost = transport_cost + accommodation_cost

        users = []
        if route.travels and route.travels.travel_id:
            users_raw = await service_locator.get_travel_serv().get_users_by_travel(route.travels.travel_id)
            users = [user for user in users_raw if user is not None]
        logger.info("archive users: ", users)
        route_dict = {
            "route_id": route.route_id,
            "start_time": route.start_time,
            "end_time": route.end_time,
            "transport": route.d_route.type_transport if route.d_route else None,
            "cost": total_cost,
            "destination_city": route.d_route.destination_city.name if route.d_route 
                                                and route.d_route.destination_city else None,
            "entertainments": route.travels.entertainments if route.travels else [],
            "accommodations": route.travels.accommodations if route.travels else [],
            "travel_id": route.travels.travel_id if route.travels else None,
            "users": users

        }
        routes_completed_data.append(route_dict)

    return templates.TemplateResponse(
        "profile_user.html",
        {
            "request": request,
            "user": profile_data,
            "active_routes": routes_active_data,
            "completed_routes": routes_completed_data,
            "current_user_id": profile_data["user"]["user_id"]
        }
    )


@user_router.get("/user.html", response_class=HTMLResponse)
async def get_all_users(request: Request, service_locator: ServiceLocator = get_sl_dep) -> HTMLResponse:
    users_data = await service_locator.get_user_contr().get_all_users()
    users = users_data.get("users", []) 
    logger.info("Получено %d пользователей", len(users))
    return templates.TemplateResponse("user.html", {"request": request, "users": users})


@user_router.post("/user/delete/{user_id}", response_class=HTMLResponse)
async def delete_user(user_id: int, service_locator: ServiceLocator = get_sl_dep) -> RedirectResponse:
    result = await service_locator.get_user_contr().delete_user(user_id)
    logger.info("Пользователь ID %d успешно удален: %s", user_id, result)
    return RedirectResponse(url="/user.html", status_code=303)