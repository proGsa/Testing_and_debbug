from __future__ import annotations

import logging

from typing import Any

from bson import Int64
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo.errors import PyMongoError

from abstract_repository.icity_repository import ICityRepository
from abstract_repository.idirectory_route_repository import IDirectoryRouteRepository
from models.directory_route import DirectoryRoute


logger = logging.getLogger(__name__)


class DirectoryRouteRepository(IDirectoryRouteRepository):
    def __init__(self, client: AsyncIOMotorClient[Any], city_repo: ICityRepository):
        self.db: AsyncIOMotorDatabase[Any] = client["travel_db"]
        self.collection = self.db['directory_routes']
        self.city_repo = city_repo
        logger.debug("Инициализация DirectoryRouteRepository для MongoDB")

    async def get_list(self) -> list[DirectoryRoute]:
        try:
            d_routes = []
            async for doc in self.collection.find().sort("_id"):
                departure_city = await self.city_repo.get_by_id(doc["departure_city_id"])
                destination_city = await self.city_repo.get_by_id(doc["arrival_city_id"])
                
                if not departure_city or not destination_city:
                    logger.warning(f"Не удалось найти города для маршрута {doc['_id']}")
                    continue
                
                d_routes.append(DirectoryRoute(
                    d_route_id=int(doc["_id"]),
                    type_transport=doc["type_transport"],
                    cost=doc["price"],
                    distance=doc["distance"],
                    departure_city=departure_city,
                    destination_city=destination_city
                ))
            
            logger.debug("Успешно получено %d справочников", len(d_routes))
            return d_routes
        except PyMongoError as e:
            logger.error("Ошибка при получении списка справочников: %s", str(e), exc_info=True)
            return []

    async def get_by_id(self, directory_route_id: int) -> DirectoryRoute | None:
        try:
            doc = await self.collection.find_one({"_id": directory_route_id})
            if not doc:
                logger.warning("Справочник с ID %d не найден", directory_route_id)
                return None
                
            departure_city = await self.city_repo.get_by_id(doc["departure_city_id"])
            destination_city = await self.city_repo.get_by_id(doc["arrival_city_id"])
            
            if not departure_city or not destination_city:
                logger.warning(f"Не удалось найти города для маршрута {doc['_id']}")
                return None
                
            logger.debug("Найден справочник ID %d", directory_route_id)
            return DirectoryRoute(
                d_route_id=int(doc["_id"]),
                type_transport=doc["type_transport"],
                cost=doc["price"],
                distance=doc["distance"],
                departure_city=departure_city,
                destination_city=destination_city
            )
        except PyMongoError as e:
            logger.error("Ошибка при получении справочника по ID %d: %s", directory_route_id, str(e), exc_info=True)
            return None

    async def add(self, directory_route: DirectoryRoute) -> DirectoryRoute:
        try:
            if not directory_route.departure_city or not directory_route.destination_city:
                logger.error("Отсутствуют данные о городах")
                raise ValueError("Both cities are required")

            last_id = await self.collection.find().sort("_id", -1).limit(1).next()
            new_id = Int64(last_id["_id"] + 1) if last_id else Int64(1)

            doc = {
                "_id": int(new_id),
                "type_transport": directory_route.type_transport,
                "price": int(directory_route.cost),
                "distance": int(directory_route.distance),
                "departure_city_id": directory_route.departure_city.city_id,
                "arrival_city_id": directory_route.destination_city.city_id
            }
            
            await self.collection.insert_one(doc)
            logger.debug("Справочник успешно добавлен с ID %s", new_id)
            directory_route.d_route_id = new_id
            return directory_route
        except DuplicateKeyError:
            logger.warning("Такой маршрут уже существует")
            raise
        except PyMongoError as e:
            logger.error("Ошибка при добавлении справочника: %s", str(e), exc_info=True)
            raise

    async def update(self, update_directory_route: DirectoryRoute) -> None:
        try:
            if not update_directory_route.d_route_id:
                logger.error("Отсутствует ID маршрута для обновления")
                raise ValueError("Route ID is required")
                
            if not update_directory_route.departure_city or not update_directory_route.destination_city:
                logger.error("Отсутствуют данные о городах")
                raise ValueError("Both cities are required")
                
            await self.collection.update_one(
                {"_id": int(update_directory_route.d_route_id)},
                {"$set": {
                    "type_transport": update_directory_route.type_transport,
                    "price": int(update_directory_route.cost),
                    "distance": int(update_directory_route.distance),
                    "departure_city_id": update_directory_route.departure_city.city_id,
                    "arrival_city_id": update_directory_route.destination_city.city_id
                }}
            )
            logger.debug("Справочник успешно обновлен")
        except PyMongoError as e:
            logger.error("Ошибка при обновлении справочника маршрутов с ID %s: %s", 
                       update_directory_route.d_route_id, str(e), exc_info=True)
            raise
            
    async def delete(self, directory_route_id: int) -> None:
        try:
            result = await self.collection.delete_one({"_id": directory_route_id})
            if result.deleted_count == 0:
                logger.warning("Справочник с ID %d не найден для удаления", directory_route_id)
            else:
                logger.debug("Справочник ID %d успешно удален", directory_route_id)
        except PyMongoError as e:
            logger.error("Ошибка при удалении справочника маршрутов с ID %d: %s", directory_route_id, str(e), exc_info=True)
            raise

    async def get_by_cities(self, from_city_id: int, to_city_id: int, type_transport: str) -> DirectoryRoute | None:
        try:
            doc = await self.collection.find_one({
                "departure_city_id": from_city_id,
                "arrival_city_id": to_city_id,
                "type_transport": type_transport
            })
            
            if not doc:
                logger.warning("Справочник маршрута между городами %d и %d не найден", from_city_id, to_city_id)
                return None
                
            departure_city = await self.city_repo.get_by_id(doc["departure_city_id"])
            destination_city = await self.city_repo.get_by_id(doc["arrival_city_id"])
            
            if not departure_city or not destination_city:
                logger.warning(f"Не удалось найти города для маршрута {doc['_id']}")
                return None
                
            logger.debug("Найден справочник ID %s", str(doc["_id"]))
            return DirectoryRoute(
                d_route_id=int(doc["_id"]),
                type_transport=type_transport,
                cost=doc["price"],
                distance=doc["distance"],
                departure_city=departure_city,
                destination_city=destination_city
            )
        except PyMongoError as e:
            logger.error("Ошибка при получении справочника маршрутов по городам: %s", str(e), exc_info=True)
            return None

    async def change_transport(self, d_route_id: int, new_transport: str) -> DirectoryRoute | None:
        current_route = await self.get_by_id(d_route_id)
        if not current_route:
            logger.warning("Маршрут с ID %d не найден", d_route_id)
            return None
        if not current_route.departure_city or not current_route.destination_city:
            logger.warning("Города в маршруте с ID %d не найдены", d_route_id)
            return None

        return await self.get_by_cities(
            from_city_id=current_route.departure_city.city_id,
            to_city_id=current_route.destination_city.city_id,
            type_transport=new_transport
        )