from __future__ import annotations

import logging

from typing import Any

from bson import Int64
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo.errors import PyMongoError

from abstract_repository.icity_repository import ICityRepository
from abstract_repository.ientertainment_repository import IEntertainmentRepository
from models.entertainment import Entertainment


logger = logging.getLogger(__name__)


class EntertainmentRepository(IEntertainmentRepository):
    def __init__(self, client: AsyncIOMotorClient[Any], city_repo: ICityRepository):
        self.db: AsyncIOMotorDatabase[Any] = client["travel_db"]
        self.entertainments = self.db["entertainments"]
        self.city_repo = city_repo
        logger.debug("Инициализация EntertainmentRepository для MongoDB")

    async def get_list(self) -> list[Entertainment]:
        try:
            entertainments = []
            async for doc in self.entertainments.find().sort("_id"):
                city = await self.city_repo.get_by_id(doc["city_id"])
                entertainments.append(
                    Entertainment(
                        entertainment_id=int(doc["_id"]),
                        duration=doc["duration"],
                        address=doc["address"],
                        event_name=doc["event_name"],
                        event_time=doc["event_time"],
                        city=city
                    )
                )
            logger.debug("Успешно получено %d развлечений", len(entertainments))
            return entertainments
        except PyMongoError as e:
            logger.error("Ошибка при получении списка развлечений: %s", str(e), exc_info=True)
            return []

    async def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        try:
            doc = await self.entertainments.find_one({"_id": entertainment_id})
            if doc:
                city = await self.city_repo.get_by_id(doc["city_id"])
                logger.debug("Найдено развлечение ID %d: %s", entertainment_id, doc["event_name"])
                return Entertainment(
                    entertainment_id=int(doc["_id"]),
                    duration=doc["duration"],
                    address=doc["address"],
                    event_name=doc["event_name"],
                    event_time=doc["event_time"],
                    city=city
                )
            logger.warning("Развлечение с ID %d не найдено", entertainment_id)
            return None
        except PyMongoError as e:
            logger.error("Ошибка при получении развлечения по ID %d: %s", entertainment_id, e)
            return None

    async def add(self, entertainment: Entertainment) -> Entertainment:
        try:
            if not entertainment.city:
                logger.error("Отсутствуют данные о городе")
                return entertainment

            city = await self.city_repo.get_by_id(entertainment.city.city_id)
            if not city:
                logger.error("Город '%s' не найден в базе данных", entertainment.city)
                return entertainment

            last_id = await self.entertainments.find().sort("_id", -1).limit(1).next()
            new_id = Int64(last_id["_id"] + 1) if last_id else Int64(1)

            doc = {
                "_id": int(new_id),
                "duration": entertainment.duration,
                "address": entertainment.address,
                "event_name": entertainment.event_name,
                "event_time": entertainment.event_time,
                "city_id": city.city_id
            }
            
            result = await self.entertainments.insert_one(doc)
            entertainment.entertainment_id = result.inserted_id
            logger.debug("Развлечение '%s' успешно добавлено с ID %s", 
                        entertainment.event_name, str(result.inserted_id))
            return entertainment
            
        except DuplicateKeyError:
            logger.warning("Развлечение с таким ID уже существует")
            return entertainment
        except PyMongoError as e:
            logger.error("Ошибка при добавлении развлечения '%s': %s", 
                        entertainment.event_name, str(e), exc_info=True)
            return entertainment

    async def update(self, update_entertainment: Entertainment) -> None:
        try:
            if not update_entertainment.city:
                logger.error("Отсутствуют данные о городе")
                return
                
            city = await self.city_repo.get_by_id(update_entertainment.city.city_id)
            if not city:
                logger.error("Город '%s' не найден в базе данных", update_entertainment.city)
                return
                
            result = await self.entertainments.update_one(
                {"_id": update_entertainment.entertainment_id},
                {
                    "$set": {
                        "duration": update_entertainment.duration,
                        "address": update_entertainment.address,
                        "event_name": update_entertainment.event_name,
                        "event_time": update_entertainment.event_time,
                        "city_id": city.city_id
                    }
                }
            )
            
            if result.modified_count == 0:
                logger.warning("Развлечение с ID %d не найдено для обновления", 
                             update_entertainment.entertainment_id)
            else:
                logger.debug("Развлечение ID %d успешно обновлено", 
                           update_entertainment.entertainment_id)
                
        except PyMongoError as e:
            logger.error("Ошибка при обновлении развлечения ID %d: %s", 
                       update_entertainment.entertainment_id, str(e), exc_info=True)

    async def delete(self, entertainment_id: int) -> None:
        try:
            result = await self.entertainments.delete_one({"_id": entertainment_id})
            if result.deleted_count == 0:
                logger.warning("Развлечение с ID %d не найдено для удаления", entertainment_id)
            else:
                logger.debug("Развлечение ID %d успешно удалено", entertainment_id)
        except PyMongoError as e:
            logger.error("Ошибка при удалении развлечения ID %d: %s", entertainment_id, str(e), exc_info=True)