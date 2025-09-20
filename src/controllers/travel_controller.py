from __future__ import annotations

import logging

from typing import Any

from fastapi import Request

from models.travel import Travel
from services.accommodation_service import AccommodationService
from services.entertainment_service import EntertainmentService
from services.travel_service import TravelService
from services.user_service import UserService


logger = logging.getLogger(__name__)


class TravelController:
    def __init__(self, travel_service: TravelService, user_service: UserService, ent_service: EntertainmentService, 
                                                                            acc_service: AccommodationService) -> None:
        self.travel_service = travel_service
        self.user_service = user_service
        self.ent_service = ent_service
        self.acc_service = acc_service
        logger.debug("Инициализация TravelController")

    async def create_new_travel(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            users = []
            for user_id in data["user_ids"]:
                if user := await self.user_service.get_by_id(user_id):
                    users.append(user)
            entertainments = [
                e for eid in data["entertainment_ids"]
                if (e := await self.ent_service.get_by_id(eid)) is not None
            ]

            accommodations = [
                a for aid in data["accommodation_ids"]
                if (a := await self.acc_service.get_by_id(aid)) is not None
            ]
            travel = Travel(
                travel_id=1,
                status=data["status"],
                users=users,
                entertainments=entertainments,
                accommodations=accommodations,
            )

            await self.travel_service.add(travel)
            logger.info("Путешествие успешно создано: %s", travel)
            return {"message": "Travel created successfully"}
        except Exception as e:
            logger.error("Ошибка при создании путешествия: %s", str(e), exc_info=True)
            raise e
        
    async def get_travel_details(self, travel_id: int) -> dict[str, Any]:
        try:
            travel = await self.travel_service.get_by_id(travel_id)
            entertainment_list = await self.travel_service.get_entertainments_by_travel(travel_id)
            accommodation_list = await self.travel_service.get_accommodations_by_travel(travel_id)
            user_list = await self.travel_service.get_users_by_travel(travel_id)
            if travel and travel.users:
                logger.info("Путешествие ID %d найдено: %s", travel_id, travel)
                return {
                    "travel": {
                        "id": travel.travel_id,
                        "status": travel.status,
                        "users": [
                            {
                                "user_id": u.user_id,
                                "fio": u.fio,
                                "email": u.email
                            }
                            for u in user_list
                        ],
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
                        ],
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
                }
            logger.warning("Путешествие ID %d не найдено", travel_id)
            return {"message": "Entertainment not found"}
        except Exception as e:
            logger.error("Ошибка при получении информации о путешествии ID: %s", str(e), exc_info=True)
            return {"message": "Error fetching details", "error": str(e)}

    async def complete_travel(self, travel_id: int) -> dict[str, Any]:
        try:
            travel_id = travel_id
            await self.travel_service.complete(travel_id)
            logger.info("Путешествие ID %d успешно завершено", travel_id)
            return {"message": "Travel completed successfully"}
        except Exception as e:
            logger.error("Ошибка при завершении путешествия ID %d: %s", travel_id, str(e), exc_info=True)
            return {"message": "Error complete travel", "error": str(e)}

    async def update_travel(self, travel_id: int, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            users = []
            for user_id in data["user_ids"]:
                if user := await self.user_service.get_by_id(user_id):
                    users.append(user)
            entertainments = [
                e for eid in data["entertainment_ids"]
                if (e := await self.ent_service.get_by_id(eid)) is not None
            ]

            accommodations = [
                a for aid in data["accommodation_ids"]
                if (a := await self.acc_service.get_by_id(aid)) is not None
            ]

            travel = Travel(
                travel_id=travel_id,
                status=data["status"],
                users=users,
                entertainments=entertainments,
                accommodations=accommodations,
            )
            await self.travel_service.update(travel)
            logger.info("Путешествие ID %d успешно обновлено", travel_id)
            return {"message": "Travel updated successfully"}
        except Exception as e:
            logger.error("Ошибка при обновлении путешествия ID %d: %s", travel_id, str(e), exc_info=True)
            return {"message": "Error updating travel", "error": str(e)}
    
    async def delete_travel(self, travel_id: int) -> dict[str, Any]:
        try:
            await self.travel_service.delete(travel_id)
            logger.info("Путешествие ID %d успешно удалено", travel_id)
            return {"message": "Travel deleted successfully"}
        except Exception as e:
            logger.error("Ошибка при удалении путешествия ID %d: %s", travel_id, str(e), exc_info=True)
            return {"message": "Error deleting travel", "error": str(e)}

    async def search_travel(self, request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
            travel_dict = data.get("search")
            
            if not travel_dict:
                logger.warning("Отсутствуют параметры поиска в запросе")
                return {"message": "Missing search parameters"}
            
            search_results = await self.travel_service.search(travel_dict)
            logger.info("Найдено %d результатов поиска", len(search_results))
            return {"search_results": search_results}
        
        except Exception as e:
            logger.error("Ошибка при поиске путешествий: %s", str(e), exc_info=True)
            return {"message": "Error searching for travel", "error": str(e)}

    async def get_all_travels(self) -> dict[str, Any]:
        try:
            travel_list = await self.travel_service.get_all_travels()
            travels = []
            for t in travel_list:
                entertainment_list = await self.travel_service.get_entertainments_by_travel(t.travel_id)
                accommodation_list = await self.travel_service.get_accommodations_by_travel(t.travel_id)
                user_list = await self.travel_service.get_users_by_travel(t.travel_id)
                if t.users:
                    travels.append({
                        "id": t.travel_id,
                        "status": t.status,
                        "users": [
                            {
                                "user_id": u.user_id,
                                "fio": u.fio
                            }
                            for u in user_list
                        ],
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
                        ],
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
                    })

            logger.info("Получено %d путешествий", len(travels))
            return {"travels": travels}
        
        except Exception as e:
            logger.error("Ошибка при получении списка путешествий: %s", str(e), exc_info=True)
            return {"message": "Error fetching travels", "error": str(e)}
