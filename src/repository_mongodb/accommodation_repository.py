from __future__ import annotations

import logging

from typing import Any

from bson import Int64
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from abstract_repository.iaccommodation_repository import IAccommodationRepository
from abstract_repository.icity_repository import ICityRepository
from models.accommodation import Accommodation


logger = logging.getLogger(__name__)


class AccommodationRepository(IAccommodationRepository):
    def __init__(self, client: AsyncIOMotorClient[Any], city_repo: ICityRepository):
        self.db: AsyncIOMotorDatabase[Any] = client["travel_db"]
        self.collection = self.db['accommodations']
        self.city_repo = city_repo
        logger.debug("Инициализация AccommodationRepository для MongoDB")

    async def get_list(self) -> list[Accommodation]:
        try:
            accommodations = []
            async for doc in self.collection.find().sort("_id"):
                city = await self.city_repo.get_by_id(doc["city_id"])
                if not city:
                    logger.warning(f"Город с ID {doc['city_id']} не найден для размещения {doc['_id']}")
                    continue
                    
                accommodations.append(Accommodation(
                    accommodation_id=int(doc["_id"]),
                    price=doc["price"],
                    address=doc["address"],
                    name=doc["name"],
                    type=doc["type"],
                    rating=doc["rating"],
                    check_in=doc["check_in"],
                    check_out=doc["check_out"],
                    city=city
                ))
            
            logger.debug("Успешно получено %d размещений", len(accommodations))
            return accommodations
        except PyMongoError as e:
            logger.error("Ошибка при получении списка размещений: %s", str(e), exc_info=True)
            raise

    async def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        try:
            doc = await self.collection.find_one({"_id": int(accommodation_id)})
            if not doc:
                logger.warning("Размещение с ID %d не найдено", accommodation_id)
                return None
                
            city = await self.city_repo.get_by_id(doc["city_id"])
            if not city:
                logger.warning(f"Город с ID {doc['city_id']} не найден для размещения {doc['_id']}")
                return None
                
            logger.debug("Найдено размещение ID %d: %s", accommodation_id, doc["name"])
            return Accommodation(
                accommodation_id=int(doc["_id"]),
                price=doc["price"],
                address=doc["address"],
                name=doc["name"],
                type=doc["type"],
                rating=doc["rating"],
                check_in=doc["check_in"],
                check_out=doc["check_out"],
                city=city
            )
        except PyMongoError as e:
            logger.error("Ошибка при получении размещения по ID %s: %s", accommodation_id, str(e), exc_info=True)
            return None

    async def add(self, accommodation: Accommodation) -> Accommodation:
        try:
            if accommodation.city is None:
                logger.error("Отсутствуют данные о городе")
                raise ValueError("City is required")
            last_id = await self.collection.find().sort("_id", -1).limit(1).next()
            new_id = Int64(last_id["_id"] + 1) if last_id else Int64(1)
            doc = {
                "_id": int(new_id),
                "price": accommodation.price,
                "address": accommodation.address,
                "name": accommodation.name,
                "type": accommodation.type,
                "rating": accommodation.rating,
                "check_in": accommodation.check_in,
                "check_out": accommodation.check_out,
                "city_id": accommodation.city.city_id
            }
            
            result = await self.collection.insert_one(doc)
            new_id = result.inserted_id
            logger.debug("Размещение '%s' успешно добавлено с ID %d", accommodation.name, new_id)
            accommodation.accommodation_id = new_id
            return accommodation
        except PyMongoError as e:
            logger.error("Ошибка при добавлении размещения '%s': %s", accommodation.name, str(e), exc_info=True)
            raise

    async def update(self, update_accommodation: Accommodation) -> None:
        try:
            if update_accommodation.city is None:
                logger.error("Отсутствуют данные о городе")
                raise ValueError("City is required")
                
            if not update_accommodation.accommodation_id:
                logger.error("Отсутствует ID размещения для обновления")
                raise ValueError("Accommodation ID is required")
                
            await self.collection.update_one(
                {"_id": int(str(update_accommodation.accommodation_id))},
                {"$set": {
                    "price": update_accommodation.price,
                    "address": update_accommodation.address,
                    "name": update_accommodation.name,
                    "type": update_accommodation.type,
                    "rating": update_accommodation.rating,
                    "check_in": update_accommodation.check_in,
                    "check_out": update_accommodation.check_out,
                    "city_id": update_accommodation.city.city_id
                }}
            )
            logger.debug("Размещение ID %s успешно обновлено", update_accommodation.accommodation_id)
        except PyMongoError as e:
            logger.error("Ошибка при обновлении размещения ID %s: %s", 
                        update_accommodation.accommodation_id, str(e), exc_info=True)
            raise
            
    async def delete(self, accommodation_id: int) -> None:
        try:
            result = await self.collection.delete_one({"_id": int(str(accommodation_id))})
            if result.deleted_count == 0:
                logger.warning("Размещение с ID %d не найдено для удаления", accommodation_id)
            else:
                logger.debug("Размещение ID %d успешно удалено", accommodation_id)
        except PyMongoError as e:
            logger.error("Ошибка при удалении размещения ID %d: %s", accommodation_id, str(e), exc_info=True)
            raise