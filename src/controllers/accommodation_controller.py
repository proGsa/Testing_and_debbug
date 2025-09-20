from __future__ import annotations

import logging

from datetime import datetime
from typing import Any

from fastapi import HTTPException
from fastapi import Request

from models.accommodation import Accommodation
from services.accommodation_service import AccommodationService
from services.city_service import CityService


logger = logging.getLogger(__name__)


class AccommodationController:
    def __init__(self, accommodation_service: AccommodationService, city_service: CityService) -> None:
        self.accommodation_service = accommodation_service
        self.city_service = city_service
        logger.debug("Инициализация AccommodationController")

    async def create_new_accommodation(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            data["accommodation_id"] = 1
            data["city"] = await self.city_service.get_by_id(data["city"])
            accommodation = Accommodation(**data)
            await self.accommodation_service.add(accommodation)
            logger.info("Проживание успешно создано: %s", accommodation)
            return {
                "message": "Accommodation created successfully",
                "accommodation_id": accommodation.accommodation_id 
            }
        except Exception as e:
            logger.error("Ошибка при создании проживания: %s", str(e), exc_info=True)
            return {"message": "Error creating accommodation", "error": str(e)}
    
    async def update_accommodation(self, accommodation_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            data["accommodation_id"] = accommodation_id
            data["city"] = await self.city_service.get_by_id(data["city"])
            accommodation = Accommodation(**data)
            await self.accommodation_service.update(accommodation)
            logger.info("Проживание ID %d успешно обновлено", accommodation_id)
            return {"message": "Accommodation updated successfully"}
        except Exception as e:
            logger.error("Ошибка при обновлении проживания ID %d: %s", accommodation_id, str(e), exc_info=True)
            return {"message": "Error updating accommodation", "error": str(e)}
    
    async def get_accommodation_details(self, accommodation_id: int,) -> dict[str, Any]:
        try:
            accommodation = await self.accommodation_service.get_by_id(accommodation_id)
            if accommodation:
                logger.info("Проживание ID %d найдено: %s", accommodation_id, accommodation)
                return {
                    "accommodation": {
                        "id": accommodation.accommodation_id,
                        "price": accommodation.price,
                        "address": accommodation.address,
                        "name": accommodation.name,
                        "type": accommodation.type,
                        "rating": accommodation.rating,
                        "check_in": accommodation.check_in.strftime('%Y-%m-%dT%H:%M'),
                        "check_out": accommodation.check_out.strftime('%Y-%m-%dT%H:%M'),
                        "city": accommodation.city
                    }
                }
            logger.warning("Проживание ID %d не найдено", accommodation_id)
            return {"message": "Accommodation not found"}
        except Exception as e:
            logger.error("Ошибка при получении информации о проживании: %s", str(e), exc_info=True)
            return {"message": "Error fetching details", "error": str(e)}

    async def get_all_accommodation(self) -> dict[str, Any]:
        try:
            accommodation_list = await self.accommodation_service.get_list()
            logger.info("Получено %d записей о проживании", len(accommodation_list))
            return {
                    "accommodations": [
                        {
                            "id": a.accommodation_id,
                            "price": a.price,
                            "address": a.address,
                            "name": a.name,
                            "type": a.type,
                            "rating": a.rating,
                            "check_in": a.check_in.isoformat(),
                            "check_out": a.check_out.isoformat(),
                            "city": a.city
                        }
                        for a in accommodation_list
                    ]
                }
        except Exception as e:
            logger.error("Ошибка при получении списка проживаний: %s", str(e), exc_info=True)
            return {"message": "Error fetching accommodations", "error": str(e)}

    async def delete_accommodation(self, accommodation_id: int) -> dict[str, Any]:
        try:
            await self.accommodation_service.delete(accommodation_id)
            logger.info("Проживание ID %d успешно удалено", accommodation_id)
            return {"message": "Accommodation deleted successfully"}
        except Exception as e:
            logger.error("Ошибка при удалении проживания ID %d: %s", accommodation_id, str(e), exc_info=True)
            return {"message": "Error deleting accommodation", "error": str(e)}
        
    async def update_accommodation_dates(self, accommodation_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            check_in = datetime.fromisoformat(data["check_in"])
            check_out = datetime.fromisoformat(data["check_out"])
            
            accommodation = await self.accommodation_service.get_by_id(accommodation_id)
            if not accommodation:
                raise HTTPException(status_code=404, detail="Accommodation not found")
            
            nights = (check_out - check_in).days
            old_nights = (accommodation.check_out - accommodation.check_in).days
            new_price = int(self.calculate_price(accommodation.price / old_nights, nights))

            accommodation.check_in = check_in
            accommodation.check_out = check_out
            accommodation.price = new_price
            
            await self.accommodation_service.update(accommodation)
            
            logger.info("Даты и цена проживания ID %d успешно обновлены", accommodation_id)
            return {
                "message": "Accommodation dates and price updated successfully",
                "updated_price": new_price
            }
            
        except Exception as e:
            logger.error("Ошибка при обновлении дат проживания ID %d: %s", 
                    accommodation_id, str(e), exc_info=True)
            raise HTTPException(status_code=400, detail=str(e))
            
    @staticmethod
    def calculate_price(base_price: float, nights: int) -> float:
        return base_price * nights