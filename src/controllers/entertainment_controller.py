from __future__ import annotations

import logging

from datetime import datetime
from json import JSONDecodeError
from typing import Any

from fastapi import HTTPException
from fastapi import Request

from models.entertainment import Entertainment
from services.city_service import CityService
from services.entertainment_service import EntertainmentService


logger = logging.getLogger(__name__)


class EntertainmentController:
    def __init__(self, entertainment_service: EntertainmentService, city_service: CityService) -> None:
        self.entertainment_service = entertainment_service
        self.city_service = city_service
        logger.debug("Инициализация EntertainmentController")

    async def create_new_entertainment(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            data["entertainment_id"] = 1
            data["city"] = await self.city_service.get_by_id(data["city"])
            entertainment = Entertainment(**data)
            entertainment = await self.entertainment_service.add(entertainment)
            logger.info("Развлечение успешно создано: %s", entertainment)
            return {
                "message": "Entertainment created successfully",
                "entertainment_id": entertainment.entertainment_id  # Вот здесь ID возвращается
            }
        except Exception as e:
            logger.error("Ошибка при создании развлечения: %s", str(e), exc_info=True)
            return {"message": "Error creating entertainment", "error": str(e)}

    async def update_entertainment(self, entertainment_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            data["entertainment_id"] = entertainment_id
            data["city"] = await self.city_service.get_by_id(data["city"])
            entertainment = Entertainment(**data)
            await self.entertainment_service.update(entertainment)
            logger.info("Развлечение ID %d успешно обновлено", entertainment_id)
            return {"message": "Entertainment updated successfully"}
        except Exception as e:
            logger.error("Ошибка при обновлении развлечения ID %d: %s", entertainment_id, str(e), exc_info=True)
            return {"message": "Error updating entertainment", "error": str(e)}
            
    async def get_entertainment_details(self, entertainment_id: int) -> dict[str, Any]:
        try:
            entertainment = await self.entertainment_service.get_by_id(entertainment_id)
            if entertainment:
                logger.info("Развлечение ID %d найдено: %s", entertainment_id, entertainment)
                return {
                    "entertainment": {
                        "id": entertainment.entertainment_id,
                        "duration": entertainment.duration,
                        "address": entertainment.address,
                        "event_name": entertainment.event_name,
                        "event_time": entertainment.event_time.isoformat(),
                        "city": entertainment.city
                        }
                }
            logger.warning("Развлечение ID %d не найдено", entertainment_id)
            return {"message": "Entertainment not found"}
        except JSONDecodeError:
            logger.warning("Некорректный JSON в теле запроса")
            return {"message": "Invalid JSON in request"}
        except Exception as e:
            logger.error("Ошибка при получении информации о развлечении: %s", str(e), exc_info=True)
            return {"message": "Error fetching details", "error": str(e)}

    async def get_all_entertainment(self) -> dict[str, Any]:
        try:
            entertainment_list = await self.entertainment_service.get_list()
            logger.info("Получено %d развлечений", len(entertainment_list))
            return {
                "entertainments": [
                    {
                        "id": e.entertainment_id,
                        "duration": e.duration,
                        "address": e.address,
                        "event_name": e.event_name,
                        "event_time": e.event_time.isoformat(),
                        "city": e.city
                    }
                    for e in entertainment_list
                ]
            }
        except Exception as e:
            logger.error("Ошибка при получении списка развлечений: %s", str(e), exc_info=True)
            return {"message": "Error fetching entertainments", "error": str(e)}

    async def delete_entertainment(self, entertainment_id: int) -> dict[str, Any]:
        try:
            await self.entertainment_service.delete(entertainment_id)
            logger.info("Развлечение ID %d успешно удалено", entertainment_id)
            return {"message": "Entertainment deleted successfully"}
        except Exception as e:
            logger.error("Ошибка при удалении развлечения ID %d: %s", entertainment_id, str(e), exc_info=True)
            return {"message": "Error deleting entertainment", "error": str(e)}
    
    async def update_entertainment_dates(self, entertainment_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            entertainment = await self.entertainment_service.get_by_id(entertainment_id)
            if not entertainment:
                raise HTTPException(status_code=404, detail="Entertainment not found")

            entertainment.event_time = datetime.fromisoformat(data["event_time"])
            entertainment.duration = data['duration']
            
            await self.entertainment_service.update(entertainment)
            
            logger.info("Даты и продолжительность мероприятия ID %d успешно обновлены", entertainment_id)
            return {
                "message": "Entertainment dates and duration updated successfully"
            }
            
        except Exception as e:
            logger.error("Ошибка при обновлении дат проживания ID %d: %s", 
                    entertainment_id, str(e), exc_info=True)
            raise HTTPException(status_code=400, detail=str(e))