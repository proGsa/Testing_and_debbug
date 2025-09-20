from __future__ import annotations

import logging

from typing import Any

from fastapi import Request

from models.directory_route import DirectoryRoute
from services.city_service import CityService
from services.directory_route_service import DirectoryRouteService


logger = logging.getLogger(__name__)


class DirectoryRouteController:
    def __init__(self, directory_route_service: DirectoryRouteService, city_service: CityService) -> None:
        self.directory_route_service = directory_route_service
        self.city_service = city_service
        logger.debug("Инициализация DirectoryRouteController")

    async def create_new_d_route(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            data["d_route_id"] = 1
            data["departure_city"] = await self.city_service.get_by_id(data["departure_city"])
            data["destination_city"] = await self.city_service.get_by_id(data["destination_city"])
            d_route = DirectoryRoute(**data)
            await self.directory_route_service.add(d_route)
            logger.info("Справочный маршрут успешно создан: %s", d_route)
            return {"message": "Directory route created successfully"}
        except Exception as e:
            logger.error("Ошибка при создании справочного маршрута: %s", str(e), exc_info=True)
            return {"message": "Error creating directory route", "error": str(e)}
    
    async def update_d_route(self, d_route_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            data["d_route_id"] = d_route_id
            data["departure_city"] = await self.city_service.get_by_id(data["departure_city"])
            data["destination_city"] = await self.city_service.get_by_id(data["destination_city"])
            d_route = DirectoryRoute(**data)
            await self.directory_route_service.update(d_route)
            logger.info("Справочный маршрут ID %d успешно обновлен", d_route_id)
            return {"message": "Directory route updated successfully"}
        except Exception as e:
            logger.error("Ошибка при обновлении справочного маршрута ID %d: %s", d_route_id, str(e), exc_info=True)
            return {"message": "Error updating directory route", "error": str(e)}
    
    async def get_d_route_details(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            d_route_id = data.get("id")
            if d_route_id is None:
                logger.warning("ID справочного маршрута не передан в запросе")
                return {"message": "Missing 'id' in request"}
            d_route = await self.directory_route_service.get_by_id(d_route_id)
            if d_route:
                logger.info("Справочный маршрут ID %d найден: %s", d_route_id, d_route)
                return {
                    "d_route": {
                        "id": d_route.d_route_id,
                        "type_transport": d_route.type_transport,
                        "cost": d_route.cost,
                        "distance": d_route.distance,
                        "departure_city": d_route.departure_city,
                        "destination_city": d_route.destination_city
                    }
                }
            logger.warning("Справочный маршрут ID %d не найден", d_route_id)
            return {"message": "Directory route not found"}
        except Exception as e:
            logger.error("Ошибка при получении информации о справочном маршруте ID: %s", 
                                                                    str(e), exc_info=True)
            return {"message": "Error fetching details", "error": str(e)}

    async def get_all_d_routes(self) -> dict[str, Any]:
        try:
            d_route_list = await self.directory_route_service.get_list()
            logger.info("Получено %d справочных маршрутов", len(d_route_list))
            return {
                    "d_routes": [
                        {
                            "id": r.d_route_id,
                            "type_transport": r.type_transport,
                            "cost": r.cost,
                            "distance": r.distance,
                            "departure_city": r.departure_city,
                            "destination_city": r.destination_city
                        }
                        for r in d_route_list
                    ]
                }
        except Exception as e:
            logger.error("Ошибка при получении списка справочных маршрутов: %s", str(e), exc_info=True)
            return {"message": "Error fetching directory routes", "error": str(e)}

    async def delete_d_route(self, d_route_id: int) -> dict[str, Any]:
        try:
            await self.directory_route_service.delete(d_route_id)
            logger.info("Справочный маршрут ID %d успешно удален", d_route_id)
            return {"message": "Directory route deleted successfully"}
        except Exception as e:
            logger.error("Ошибка при удалении справочного маршрута ID %d: %s", d_route_id, str(e), exc_info=True)
            return {"message": "Error deleting directory route", "error": str(e)}