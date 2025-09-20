from __future__ import annotations

import logging

from typing import Any

from bson import Int64
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo.errors import PyMongoError

from abstract_repository.iaccommodation_repository import IAccommodationRepository
from abstract_repository.ientertainment_repository import IEntertainmentRepository
from abstract_repository.itravel_repository import ITravelRepository
from abstract_repository.iuser_repository import IUserRepository
from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.travel import Travel
from models.user import User


logger = logging.getLogger(__name__)


class TravelRepository(ITravelRepository):
    def __init__(self, client: AsyncIOMotorClient[Any], user_repo: IUserRepository, ent_repo: IEntertainmentRepository, acc_repo: IAccommodationRepository):
        self.db: AsyncIOMotorDatabase[Any] = client["travel_db"]
        self.travels = self.db["travels"]
        self.user_repo = user_repo
        self.ent_repo = ent_repo
        self.acc_repo = acc_repo
        logger.debug("Инициализация TravelRepository для MongoDB")

    async def get_accommodations_by_travel(self, travel_id: int) -> list[Accommodation]:
        try:
            travel = await self.travels.find_one({"_id": travel_id})
            if not travel:
                return []
                
            accommodations = []
            for acc_id in travel.get("accommodations", []):
                acc = await self.acc_repo.get_by_id(int(acc_id))
                if acc:
                    accommodations.append(acc)
            
            logger.debug("Получено %d размещений для путешествия ID %d", len(accommodations), travel_id)
            return accommodations
        except PyMongoError as e:
            logger.error("Ошибка при получении размещений: %s", str(e), exc_info=True)
            return []

    async def get_users_by_travel(self, travel_id: int) -> list[User]:
        try:
            travel = await self.travels.find_one({"_id": travel_id})
            if not travel:
                return []
                
            users = []
            for user_id in travel.get("users", []):
                user = await self.user_repo.get_by_id(user_id)
                if user:
                    users.append(user)
            
            logger.debug("Получено %d пользователей для путешествия ID %d", len(users), travel_id)
            return users
        except PyMongoError as e:
            logger.error("Ошибка при получении пользователей: %s", str(e), exc_info=True)
            return []

    async def get_entertainments_by_travel(self, travel_id: int) -> list[Entertainment]:
        try:
            travel = await self.travels.find_one({"_id": travel_id})
            if not travel:
                return []
                
            entertainments = []
            for ent_id in travel.get("entertainments", []):
                ent = await self.ent_repo.get_by_id(ent_id)
                if ent:
                    entertainments.append(ent)
            
            logger.debug("Получено %d развлечений для путешествия ID %d", len(entertainments), travel_id)
            return entertainments
        except PyMongoError as e:
            logger.error("Ошибка при получении развлечений: %s", str(e), exc_info=True)
            return []

    async def get_list(self) -> list[Travel]:
        try:
            travels = []
            async for doc in self.travels.find().sort("_id"):
                travels.append(Travel(
                    travel_id=int(doc["_id"]),
                    status=doc["status"],
                    users=await self.get_users_by_travel(int(doc["_id"])),
                    entertainments=await self.get_entertainments_by_travel(int(doc["_id"])),
                    accommodations=await self.get_accommodations_by_travel(int(doc["_id"]))
                ))
            logger.debug("Получено %d записей о путешествиях", len(travels))
            return travels
        except PyMongoError as e:
            logger.error("Ошибка при получении списка: %s", str(e), exc_info=True)
            return []

    async def get_travel_by_route_id(self, route_id: int) -> Travel | None:
        try:
            route = await self.db["routes"].find_one({"_id": route_id})
            if not route:
                return None
                
            travel = await self.travels.find_one({"_id": route["travel"]["_id"]})
            if not travel:
                return None
                
            logger.debug("Путешествие с route ID %d успешно найдено", route_id)
            return Travel(
                travel_id=travel["_id"],
                status=travel["status"],
                users=await self.get_users_by_travel(travel["_id"]),
                entertainments=await self.get_entertainments_by_travel(travel["_id"]),
                accommodations=await self.get_accommodations_by_travel(travel["_id"])
            )
        except PyMongoError as e:
            logger.error("Ошибка при поиске по route ID: %s", str(e), exc_info=True)
            return None

    async def get_by_id(self, travel_id: int) -> Travel | None:
        try:
            travel = await self.travels.find_one({"_id": travel_id})
            if not travel:
                return None
                
            logger.debug("Найдено путешествие ID %d", travel_id)
            return Travel(
                travel_id=travel["_id"],
                status=travel["status"],
                users=await self.get_users_by_travel(travel_id),
                entertainments=await self.get_entertainments_by_travel(travel_id),
                accommodations=await self.get_accommodations_by_travel(travel_id)
            )
        except PyMongoError as e:
            logger.error("Ошибка при получении по ID: %s", str(e), exc_info=True)
            return None

    async def add(self, travel: Travel) -> Travel:
        try:
            last_id = await self.travels.find().sort("_id", -1).limit(1).next()
            new_id = Int64(last_id["_id"] + 1) if last_id else Int64(1)
            doc = {
                "_id": int(new_id),
                "status": travel.status,
                "users": [user.user_id for user in travel.users],
                "entertainments": [ent.entertainment_id for ent in travel.entertainments],
                "accommodations": [acc.accommodation_id for acc in travel.accommodations]
            }
            
            result = await self.travels.insert_one(doc)
            travel.travel_id = result.inserted_id
            logger.debug("Путешествие создано с ID %s", str(result.inserted_id))
            return travel
        except DuplicateKeyError:
            logger.warning("Дублирующаяся запись о путешествии")
            return travel
        except PyMongoError as e:
            logger.error("Ошибка при добавлении: %s", str(e), exc_info=True)
            return travel

    async def update(self, update_travel: Travel) -> None:
        try:
            result = await self.travels.update_one(
                {"_id": update_travel.travel_id},
                {"$set": {
                    "status": update_travel.status,
                    "users": [user.user_id for user in update_travel.users] if update_travel.users else [],
                    "entertainments": [ent.entertainment_id for ent in update_travel.entertainments] if update_travel.entertainments else [],
                    "accommodations": [acc.accommodation_id for acc in update_travel.accommodations] if update_travel.accommodations else []
                }}
            )
            
            if result.modified_count == 0:
                logger.warning("Путешествие ID %d не найдено для обновления", update_travel.travel_id)
            else:
                logger.debug("Путешествие ID %d успешно обновлено", update_travel.travel_id)
        except PyMongoError as e:
            logger.error("Ошибка при обновлении: %s", str(e), exc_info=True)

    async def delete(self, travel_id: int) -> None:
        try:
            result = await self.travels.delete_one({"_id": travel_id})
            if result.deleted_count == 0:
                logger.warning("Путешествие ID %d не найдено для удаления", travel_id)
            else:
                logger.debug("Путешествие ID %d удалено", travel_id)
        except PyMongoError as e:
            logger.error("Ошибка при удалении: %s", str(e), exc_info=True)

    async def search(self, travel_dict: dict[str, Any]) -> list[Travel]:
        try:
            query = {"status": {"$ne": "Завершен"}}
            
            if "start_time" in travel_dict:
                query["routes.start_time"] = {"$gte": travel_dict["start_time"]}
            
            if "end_time" in travel_dict:
                query["routes.end_time"] = {"$lte": travel_dict["end_time"]}
            
            if "departure_city" in travel_dict:
                query["routes.d_route.departure_city_id"] = travel_dict["departure_city"]
            
            if "arrival_city" in travel_dict:
                query["routes.d_route.arrival_city_id"] = travel_dict["arrival_city"]
            
            if "entertainment_name" in travel_dict:
                query["entertainments.event_name"] = {"$regex": travel_dict["entertainment_name"], "$options": "i"}
            
            travels = []
            async for doc in self.travels.find(query):
                travels.append(Travel(
                    travel_id=int(doc["_id"]),
                    status=doc["status"],
                    users=await self.get_users_by_travel(int(doc["_id"])),
                    entertainments=await self.get_entertainments_by_travel(int(doc["_id"])),
                    accommodations=await self.get_accommodations_by_travel(int(doc["_id"]))
                ))
            
            logger.debug("Успешно найдено %d путешествий с параметрами", len(travels))
            return travels
        except PyMongoError as e:
            logger.error("Ошибка при поиске: %s", str(e), exc_info=True)
            return []

    async def complete(self, travel_id: int) -> None:
        try:
            result = await self.travels.update_one(
                {"_id": travel_id},
                {"$set": {"status": "Завершен"}}
            )
            
            if result.modified_count == 0:
                logger.warning("Путешествие ID %d не найдено для завершения", travel_id)
            else:
                logger.debug("Путешествие ID %d успешно завершено", travel_id)
        except PyMongoError as e:
            logger.error("Ошибка при завершении: %s", str(e), exc_info=True)

    async def link_entertainments(self, travel_id: int, entertainment_ids: list[int]) -> None:
        try:
            result = await self.travels.update_one(
                {"_id": travel_id},
                {"$set": {"entertainments": entertainment_ids}}
            )
            
            if result.modified_count == 0:
                logger.warning("Путешествие ID %d не найдено", travel_id)
            else:
                logger.debug("Успешно связаны развлечения с путешествием")
        except PyMongoError as e:
            logger.error("Ошибка при связывании развлечений: %s", str(e), exc_info=True)
            raise

    async def link_accommodations(self, travel_id: int, accommodation_ids: list[int]) -> None:
        try:
            result = await self.travels.update_one(
                {"_id": travel_id},
                {"$set": {"accommodations": accommodation_ids}}
            )
            
            if result.modified_count == 0:
                logger.warning("Путешествие ID %d не найдено", travel_id)
            else:
                logger.debug("Успешно связаны размещения с путешествием")
        except PyMongoError as e:
            logger.error("Ошибка при связывании размещений: %s", str(e), exc_info=True)
            raise

    async def get_travels_for_user(self, user_id: int, status: str) -> list[Travel]:
        try:
            travels = []
            async for doc in self.travels.find({
                "status": status,
                "users": user_id
            }):
                travels.append(Travel(
                    travel_id=int(doc["_id"]),
                    status=doc["status"],
                    users=await self.get_users_by_travel(int(doc["_id"])),
                    entertainments=await self.get_entertainments_by_travel(int(doc["_id"])),
                    accommodations=await self.get_accommodations_by_travel(int(doc["_id"]))
                ))
            
            logger.debug("Успешно найдены путешествия по user_id = %d, status = %s", user_id, status)
            return travels
        except PyMongoError as e:
            logger.error("Ошибка при поиске: %s", str(e), exc_info=True)
            return []

    async def link_users(self, travel_id: int, user_ids: list[int]) -> None:
        try:
            result = await self.travels.update_one(
                {"_id": travel_id},
                {"$set": {"users": user_ids}}
            )
            
            if result.modified_count == 0:
                logger.warning("Путешествие ID %d не найдено", travel_id)
            else:
                logger.debug("Успешно связаны пользователи с путешествием")
        except PyMongoError as e:
            logger.error("Ошибка при связывании пользователей: %s", str(e), exc_info=True)
            raise