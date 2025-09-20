from __future__ import annotations

import logging

from typing import Any

from fastapi import Request

from models.city import City
from services.city_service import CityService


logger = logging.getLogger(__name__)


class CityController:
    def __init__(self, city_service: CityService) -> None:
        self.city_service = city_service
        logger.debug("Инициализация CityController")
        
    async def create_new_city(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            data["city_id"] = 1
            city = City(**data)
            await self.city_service.add(city)
            logger.info("Город успешно создан: %s", city)
            return {"message": "City created successfully"}
        except Exception as e:
            logger.error("Ошибка при создании города: %s", str(e), exc_info=True)
            return {"message": "Error creating city", "error": str(e)}
    
    async def update_city(self, city_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            data["city_id"] = city_id
            city = City(**data)
            await self.city_service.update(city)
            logger.info("Город ID %d успешно обновлен", city_id)
            return {"message": "City updated successfully"}
        except Exception as e:
            logger.error("Ошибка при обновлении города ID %d: %s", city_id, str(e), exc_info=True)
            return {"message": "Error updating city", "error": str(e)}
    
    async def get_city_details(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            city_id = data.get("id")
            if city_id is None:
                logger.warning("ID города не передан в запросе")
                return {"message": "Missing 'id' in request"}
            city = await self.city_service.get_by_id(city_id)
            if city:
                logger.info("Город ID %d найден: %s", city_id, city)
                return {
                    "city": {
                        "id": city.city_id,
                        "name": city.name
                    }
                }
            logger.warning("Город ID %d не найден", city_id)
            return {"message": "Directory route not found"}
        except Exception as e:
            logger.error("Ошибка при получении информации о городе: %s", str(e), exc_info=True)
            return {"message": "Error fetching details", "error": str(e)}

    async def get_all_cities(self) -> dict[str, Any]:
        try:
            city_list = await self.city_service.get_all_cities()
            logger.info("Получено %d городов", len(city_list))
            return {
                    "cities": [
                        {
                            "id": c.city_id,
                            "name": c.name
                        }
                        for c in city_list
                    ]
                }
        except Exception as e:
            logger.error("Ошибка при получении списка городов: %s", str(e), exc_info=True)
            return {"message": "Error fetching cities", "error": str(e)}

    async def delete_city(self, city_id: int) -> dict[str, Any]:
        try:
            await self.city_service.delete(city_id)
            logger.info("Город ID %d успешно удален", city_id)
            return {"message": "Directory route deleted successfully"}
        except Exception as e:
            logger.error("Ошибка при удалении города ID %d: %s", city_id, str(e), exc_info=True)
            return {"message": "Error deleting city", "error": str(e)}