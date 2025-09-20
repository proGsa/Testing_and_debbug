from __future__ import annotations

import logging

from typing import Any

from bson import Int64
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo.errors import PyMongoError

from abstract_repository.icity_repository import ICityRepository
from models.city import City


logger = logging.getLogger(__name__)


class CityRepository(ICityRepository):
    def __init__(self, client: AsyncIOMotorClient[Any]):
        self.db: AsyncIOMotorDatabase[Any] = client["travel_db"]
        self.collection = self.db['cities']
        logger.debug("Инициализация CityRepository для MongoDB")

    async def get_list(self) -> list[City]:
        try:
            cities = []
            async for doc in self.collection.find().sort("_id"):
                cities.append(City(
                    city_id=int(doc["_id"]),
                    name=doc["name"]
                ))
            
            logger.debug("Успешно получено %d городов", len(cities))
            return cities
        except PyMongoError as e:
            logger.error("Ошибка при получении списка городов: %s", str(e), exc_info=True)
            raise 

    async def get_by_id(self, city_id: int) -> City | None:
        try:
            doc = await self.collection.find_one({"_id": int(str(city_id))})
            if not doc:
                logger.warning("Город с ID %s не найден", city_id)
                return None
                
            logger.debug("Найден город ID %d: %s", city_id, doc["name"])
            return City(
                city_id=int(doc["_id"]),
                name=doc["name"]
            )
        except PyMongoError as e:
            logger.error("Ошибка при получении города по ID %s: %s", city_id, str(e), exc_info=True)
            return None

    async def add(self, city: City) -> City:
        try:
            last_id = await self.collection.find().sort("_id", -1).limit(1).next()
            new_id = Int64(last_id["_id"] + 1) if last_id else Int64(1)
            doc = {"_id": int(new_id), "name": city.name}
            
            result = await self.collection.insert_one(doc)
            new_id = result.inserted_id
            logger.debug("Город '%s' успешно добавлен с ID %d", city.name, new_id)
            city.city_id = new_id
            return city
        except DuplicateKeyError:
            logger.warning("Город с именем '%s' уже существует", city.name)
            raise
        except PyMongoError as e:
            logger.error("Ошибка при добавлении города '%s': %s", city.name, str(e), exc_info=True)
            raise

    async def update(self, update_city: City) -> None:
        try:
            if not update_city.city_id:
                logger.error("Отсутствует ID города для обновления")
                raise ValueError("City ID is required")
                
            await self.collection.update_one(
                {"_id": int(str(update_city.city_id))},
                {"$set": {
                    "name": update_city.name
                }}
            )
            logger.debug("Город ID %s успешно обновлен", update_city.city_id)
        except PyMongoError as e:
            logger.error("Ошибка при обновлении города ID %s: %s", 
                       update_city.city_id, str(e), exc_info=True)
            raise

    async def delete(self, city_id: int) -> None:
        try:
            result = await self.collection.delete_one({"_id": int(str(city_id))})
            if result.deleted_count == 0:
                logger.warning("Город с ID %d не найден для удаления", city_id)
            else:
                logger.debug("Город ID %d успешно удален", city_id)
        except PyMongoError as e:
            logger.error("Ошибка при удалении города ID %d: %s", city_id, str(e), exc_info=True)
            raise