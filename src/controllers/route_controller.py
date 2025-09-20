from __future__ import annotations

import logging

from datetime import datetime
from typing import Any

from fastapi import HTTPException
from fastapi import Request

from models.route import Route
from models.travel import Travel
from services.accommodation_service import AccommodationService
from services.directory_route_service import DirectoryRouteService
from services.entertainment_service import EntertainmentService
from services.route_service import RouteService
from services.travel_service import TravelService
from services.user_service import UserService


logger = logging.getLogger(__name__)


class RouteController:
    def __init__(self, route_service: RouteService, travel_service: TravelService, 
            d_route_service: DirectoryRouteService, user_service: UserService, 
                    ent_service: EntertainmentService, acc_service: AccommodationService) -> None:
        self.route_service = route_service
        self.travel_service = travel_service
        self.d_route_service = d_route_service
        self.user_service = user_service
        self.ent_service = ent_service
        self.acc_service = acc_service
        logger.debug("Инициализация RouteController")

    async def create_new_route_user(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            try:
                data['start_time'] = datetime.strptime(data['start_date'], '%d.%m.%Y')
                data['end_time'] = datetime.strptime(data['end_date'], '%d.%m.%Y')
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            
            d_route = await self.d_route_service.get_by_cities(
                int(data['departure_city']),
                int(data['destination_city']),
                data['transport']
            )
            
            if not d_route:
                raise HTTPException(
                    status_code=400,
                    detail=f"Маршрут между городами {data['departure_city']} и {data['destination_city']} не найден"
                )
            
            data['d_route'] = d_route
            data['route_id'] = 1
            data["type"] = "Свои"
            logger.info("Создание маршрута с данными: %s", data)
            user = await self.user_service.get_by_id(int(data.get('user_id')))
            if not user:
                raise 
            travel = Travel(
                travel_id=1,
                status="В процессе",
                users=[user],
                entertainments=[
                    e for eid in data.get('entertainments[]')
                    if (e := await self.ent_service.get_by_id(int(eid))) is not None
                ],
                accommodations=[
                    a for aid in data.get('accommodations[]')
                    if (a := await self.acc_service.get_by_id(int(aid))) is not None
                ]
            )
            data['travels'] = await self.travel_service.add(travel)
            
            route = Route(**data)
            created_route = await self.route_service.add(route)
            
            logger.info("Маршрут успешно создан, ID: %d", created_route.route_id)
            return {
                "message": "Route created successfully",
                "route_id": created_route.route_id,
                "d_route_id": d_route.d_route_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Ошибка при создании маршрута: %s", str(e), exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при создании маршрута: {e!s}"
            )

    async def create_new_route(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            d_route_id = data.get('d_route_id')
            data['d_route'] = await self.d_route_service.get_by_id(d_route_id)
            travel_id = data.get('travel_id')
            data['travels'] = await self.travel_service.get_by_id(travel_id)
            data["route_id"] = 1
            route = Route(**data)
            await self.route_service.add(route)
            logger.info("Маршрут успешно создан: %s", route)
            return {"message": "Route created successfully"}
        except Exception as e:
            logger.error("Ошибка при создании маршрута: %s", str(e), exc_info=True)
            return {"message": "Error creating route", "error": str(e)}

    async def add_new_city(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel_id = int(data.get("travel_id"))
            new_city_id = int(data.get("new_city_id"))
            after_city_id = int(data.get("after_city_id"))
            transport = data.get("transport")

            if not travel_id or not new_city_id or not after_city_id:
                logger.warning("Отсутствуют обязательные поля в запросе")
                return {"message": "Missing required fields in request"}

            await self.route_service.insert_city_after(travel_id, new_city_id, after_city_id, transport)
            logger.info("Город ID %d успешно добавлен в маршрут после города  %d", 
                                                                            new_city_id, after_city_id)
            return {"message": "City added to route successfully"}
        except Exception as e:
            logger.error("Ошибка при добавлении города в маршрут: %s", str(e), exc_info=True)
            return {"message": "Error adding city to route", "error": str(e)}
       
    async def get_route_parts(self, route_id: int) -> list[dict[str, Any]]:
        return await self.route_service.get_route_parts(route_id)

    async def delete_city_from_route(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            city_id = data.get("city_id")
            travel_id = data.get("travel_id")
            
            if not city_id or not travel_id:
                logger.warning("Недостаточно данных в запросе: city_id=%s, travel_id=%s", city_id, travel_id)
                return {
                    "success": False,
                    "message": "Требуются city_id и travel_id"
                }
            
            try:
                city_id = int(city_id)
                travel_id = int(travel_id)
            except (TypeError, ValueError) as e:
                logger.warning("Некорректные ID в запросе: %s", str(e))
                return {
                    "success": False,
                    "message": "ID должны быть целыми числами"
                }
            
            await self.route_service.delete_city_from_route(travel_id, city_id)
            
            logger.info("Город ID %d успешно удален из маршрута travel_id=%d", city_id, travel_id)
            return {
                "success": True,
                "message": f"Город {city_id} удален из маршрута"
            }
            
        except ValueError as e:
            logger.warning("Ошибка валидации: %s", str(e))
            return {
                "success": False,
                "message": str(e),
                "error": "validation_error"
            }
        except Exception as e:
            logger.error("Ошибка при удалении города из маршрута: %s", str(e), exc_info=True)
            return {
                "success": False,
                "message": "Внутренняя ошибка сервера",
                "error": str(e)
            }
    
    async def update_route(self, route_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            d_route_id = data.get('d_route_id')
            data['d_route'] = await self.d_route_service.get_by_id(d_route_id)
            travel_id = data.get('travel_id')
            data['travels'] = await self.travel_service.get_by_id(travel_id)
            data["route_id"] = route_id
            route = Route(**data)
            await self.route_service.update(route)
            logger.info("Маршрут ID %d успешно обновлен", route_id)
            return {"message": "Route updated successfully"}
        except Exception as e:
            logger.error("Ошибка при обновлении маршрута ID %d: %s", route_id, str(e), exc_info=True)
            return {"message": "Error updating route", "error": str(e)}
 
    async def change_transport(self, route_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            new_transport = data.get("transport")
            d_route_id = data.get("d_route_id")
            if not route_id or not new_transport:
                logger.warning("Отсутствуют обязательные поля в запросе")
                return {"message": "Missing required fields in request"}
            new_route = await self.route_service.change_transport(d_route_id, route_id, new_transport)
            logger.info("Транспорт в маршруте ID %d успешно изменен на %s", route_id, new_transport)
            if new_route is None or new_route.d_route is None:
                logger.error("Маршрут с ID %d не был обновлен", route_id)
                return {"message": "Error updating transport, route not found"}
            return {"message": "Transport updated successfully", "d_route_id": new_route.d_route.d_route_id}
        except Exception as e:
            logger.error("Ошибка при изменении транспорта в маршруте ID %d: %s", route_id, str(e), exc_info=True)
            return {"message": "Error updating transport", "error": str(e)}
    
    async def get_route_details(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            route_id = data.get("id")
            if route_id is None:
                logger.warning("ID маршрута не передан в запросе")
                return {"message": "Missing 'id' in request"}
            route = await self.route_service.get_by_id(route_id)
            if route and route.d_route is not None and route.travels is not None:
                logger.info("Маршрут ID %d найден: %s", route_id, route)
                return {
                    "route": {
                        "id": route.route_id,
                        "d_route_id": route.d_route.d_route_id,
                        "travel_id": route.travels.travel_id,
                        "start_time": route.start_time,
                        "end_time": route.end_time,
                        "route_id": route.route_id,
                        "type": route.type
                    }
                }
            logger.warning("Маршрут ID %d не найден", route_id)
            return {"message": "Route not found"}
        except Exception as e:
            logger.error("Ошибка при получении информации о маршруте ID: %s", str(e), exc_info=True)
            return {"message": "Error fetching details", "error": str(e)}

    async def delete_route(self, route_id: int) -> dict[str, Any]:
        try:
            await self.route_service.delete(route_id)
            logger.info("Маршрут ID %d успешно удален", route_id)
            return {"message": "Route deleted successfully"}
        except Exception as e:
            logger.error("Ошибка при удалении маршрута ID %d: %s", route_id, str(e), exc_info=True)
            return {"message": "Error deleting route", "error": str(e)}
    
    async def get_all_routes(self) -> dict[str, Any]:
        try:
            route_list = await self.route_service.get_all_routes()
            routes = []
            for r in route_list:
                if r and r.d_route and r.travels:
                    travel_users = await self.travel_service.get_users_by_travel(r.travels.travel_id)
                    routes.append({
                        "id": r.route_id,
                        "start_time": r.start_time.isoformat() if r.start_time else None,
                        "end_time": r.end_time.isoformat() if r.end_time else None,
                        "type": r.type,
                        
                        "d_route": {
                            "id": r.d_route.d_route_id,
                            "type_transport": r.d_route.type_transport,
                            "cost": r.d_route.cost,
                            "distance": r.d_route.distance,
                            "departure_city": r.d_route.departure_city.name if r.d_route.departure_city else None,
                            "destination_city": r.d_route.destination_city.name if r.d_route.destination_city else None
                        } if r.d_route else None,
                        
                        "travel": {
                            "id": r.travels.travel_id,
                            "status": r.travels.status,
                            "users": [
                                {
                                    "id": u.user_id,
                                    "fio": u.fio,
                                    "email": u.email
                                }   
                                for u in travel_users
                            ],
                            "entertainments": [
                                {
                                    "id": e.entertainment_id,
                                    "event_name": e.event_name,
                                    "address": e.address,
                                    "duration": e.duration,
                                    "event_time": e.event_time.isoformat(),
                                    "city": e.city
                                }
                                for e in (await self.travel_service.get_entertainments_by_travel(r.travels.travel_id))
                            ],
                            "accommodations": [
                                {
                                    "id": a.accommodation_id,
                                    "name": a.name,
                                    "address": a.address,
                                    "price": a.price,
                                    "type": a.type,
                                    "rating": a.rating,
                                    "check_in": a.check_in.isoformat(),
                                    "check_out": a.check_out.isoformat(),
                                    "city": a.city
                                }
                                for a in (await self.travel_service.get_accommodations_by_travel(r.travels.travel_id))
                            ]
                        } if r.travels else None
                    })
            logger.info("Получено %d маршрутов", len(routes))
            return {"routes": routes}
        except Exception as e:
            logger.error("Ошибка при получении списка маршрутов: %s", str(e), exc_info=True)
            return {"message": "Error fetching routes", "error": str(e)}

    async def change_travel_duration(self, route_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            new_end_date = data.get('new_end_date')
            if not new_end_date:
                raise HTTPException(status_code=400, detail="new_end_date is required")
            route_data = await self.route_service.get_by_id(route_id)
            if not route_data:
                return {"message": "Route not found", "error": f"Route with id {route_id} not found"}
            current_end_date = route_data.end_time
            try:
                new_end_date = datetime.strptime(new_end_date, "%Y-%m-%d")
            except ValueError:
                return {
                    "message": "Invalid date format",
                    "error": "new_end_date must be in YYYY-MM-DD format"
                }
            if new_end_date <= current_end_date:
                return {
                    "message": "Invalid date", 
                    "error": f"New end date {new_end_date} must be after current end date {current_end_date}"
                }
            route_data.end_time = new_end_date
            await self.route_service.update(route_data)
            
            logger.info("Маршрут ID %d успешно продлен до %s", route_id, new_end_date)
            return {
                "message": "Route updated successfully",
                "route_id": route_id,
                "new_end_date": new_end_date
            }
        except Exception as e:
            logger.error("Ошибка при продлении маршрута ID %d: %s", route_id, str(e), exc_info=True)
            return {"message": "Error updating route", "error": str(e)}
    
    async def join_to_trip(self, route_id: int, request: Request) -> dict[str, Any]:
        data = await request.json()
        user_id = data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        user = await self.user_service.get_by_id(user_id)
        route = await self.route_service.get_by_id(route_id)
        if not route:
            return {"message": "Route not found"}
        route.type = "Свои"
        if route.travels:
            current_users = await self.travel_service.get_users_by_travel(route.travels.travel_id)
    
        if user is not None and any(u.user_id == user.user_id for u in current_users if u is not None):
            raise HTTPException(status_code=400, detail="User already joined this trip")
        if route.travels and user:
            await self.travel_service.link_users(route.travels.travel_id, [u.user_id for u in current_users] + [user.user_id])
    
        await self.route_service.add(route)

        logger.info(f"Пользователь {user_id} присоединился к маршруту {route_id}")
        return {
            "message": "Вы успешно присоединились к маршруту",
            "route_id": route_id,
            "new_type": "Свои"
        }
