from __future__ import annotations

import logging

from datetime import timedelta
from typing import Any

from bson import Int64
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo.errors import PyMongoError

from abstract_repository.idirectory_route_repository import IDirectoryRouteRepository
from abstract_repository.iroute_repository import IRouteRepository
from abstract_repository.itravel_repository import ITravelRepository
from models.directory_route import DirectoryRoute
from models.route import Route


logger = logging.getLogger(__name__)


class RouteRepository(IRouteRepository):
    def __init__(self, client: AsyncIOMotorClient[Any], d_route_repo: IDirectoryRouteRepository, travel_repo: ITravelRepository):
        self.db: AsyncIOMotorDatabase[Any] = client["travel_db"]
        self.routes = self.db["routes"]
        self.d_route_repo = d_route_repo
        self.travel_repo = travel_repo
        logger.debug("Инициализация RouteRepository для MongoDB")

    async def get_list(self) -> list[Route]:
        try:
            routes = []
            async for doc in self.routes.find():
                d_route_doc = await self.d_route_repo.get_by_id(doc["d_route"]["_id"])
                travel_doc = await self.travel_repo.get_by_id(doc["travel"]["_id"])
                
                routes.append(Route(
                    route_id=int(doc["_id"]),
                    d_route=d_route_doc,
                    travels=travel_doc,
                    start_time=doc["start_time"],
                    end_time=doc["end_time"],
                    type=doc["type"]
                ))
            logger.debug("Успешно получено %d маршрутов", len(routes))
            return routes
        except PyMongoError as e:
            logger.error("Ошибка при получении списка маршрутов: %s", str(e), exc_info=True)
            return []

    async def get_by_id(self, route_id: int) -> Route | None:
        try:
            doc = await self.routes.find_one({"_id": route_id})
            if doc:
                d_route_doc = await self.d_route_repo.get_by_id(doc["d_route"]["_id"])
                travel_doc = await self.travel_repo.get_by_id(doc["travel"]["_id"])
                
                logger.debug("Найден маршрут ID %d", route_id)
                return Route(
                    route_id=int(doc["_id"]),
                    d_route=d_route_doc,
                    travels=travel_doc,
                    start_time=doc["start_time"],
                    end_time=doc["end_time"],
                    type=doc["type"]
                )
            logger.warning("Маршрут с ID %d не найден", route_id)
            return None
        except PyMongoError as e:
            logger.error("Ошибка при получении маршрута по ID %d: %s", route_id, str(e), exc_info=True)
            return None

    async def add(self, route: Route) -> Route:
        try:
            if not route.travels:
                logger.error("Отсутствуют данные о путешествии")
                return route
            if not route.d_route:
                logger.error("Отсутствуют данные о справочнике путешествий")
                return route
                
            last_id = await self.routes.find().sort("_id", -1).limit(1).next()
            new_id = Int64(last_id["_id"] + 1) if last_id else Int64(1)
            
            doc = {
                "_id": int(new_id),
                "d_route": {"_id": route.d_route.d_route_id},
                "travel": {"_id": route.travels.travel_id},
                "start_time": route.start_time,
                "end_time": route.end_time,
                "type": route.type
            }
            
            result = await self.routes.insert_one(doc)
            route.route_id = int(str(result.inserted_id))
            logger.debug("Маршрут успешно добавлен с ID %s", str(result.inserted_id))
            return route
            
        except DuplicateKeyError:
            logger.warning("Маршрут уже существует в базе данных")
            return route
        except PyMongoError as e:
            logger.error("Ошибка при добавлении маршрута: %s", str(e), exc_info=True)
            return route

    async def update(self, update_route: Route) -> None:
        try:
            if not update_route.travels:
                logger.error("Отсутствуют данные о путешествии для обновления")
                return
            if not update_route.d_route:
                logger.error("Отсутствуют данные о справочнике путешествий для обновления")
                return
                
            result = await self.routes.update_one(
                {"_id": update_route.route_id},
                {
                    "$set": {
                        "d_route": {"_id": update_route.d_route.d_route_id},
                        "travel": {"_id": update_route.travels.travel_id},
                        "start_time": update_route.start_time,
                        "end_time": update_route.end_time,
                        "type": update_route.type
                    }
                }
            )
            
            if result.modified_count == 0:
                logger.warning("Маршрут с ID %d не найден для обновления", update_route.route_id)
            else:
                logger.debug("Маршрут ID %d успешно обновлен", update_route.route_id)
                
        except PyMongoError as e:
            logger.error("Ошибка при обновлении маршрута ID %d: %s", 
                       update_route.route_id, str(e), exc_info=True)

    async def delete(self, route_id: int) -> None:
        try:
            result = await self.routes.delete_one({"_id": route_id})
            if result.deleted_count == 0:
                logger.warning("Маршрут с ID %d не найден для удаления", route_id)
            else:
                logger.debug("Маршрут ID %d успешно удален", route_id)
        except PyMongoError as e:
            logger.error("Ошибка при удалении маршрута ID %d: %s", route_id, str(e), exc_info=True)

    async def get_routes_by_travel_id_ordered(self, travel_id: int) -> list[Route]:
        try:
            routes = []
            async for doc in self.routes.find({"travel._id": travel_id}).sort("start_time"):
                d_route_doc = await self.d_route_repo.get_by_id(doc["d_route"]["_id"])
                travel_doc = await self.travel_repo.get_by_id(doc["travel"]["_id"])
                
                routes.append(Route(
                    route_id=int(doc["_id"]),
                    d_route=d_route_doc,
                    travels=travel_doc,
                    start_time=doc["start_time"],
                    end_time=doc["end_time"],
                    type=doc["type"]
                ))
            
            logger.debug("Маршрут с travel ID %d успешно найден", travel_id)
            return routes
        except PyMongoError as e:
            logger.error("Ошибка при получении маршрута с travel ID %d: %s", travel_id, str(e), exc_info=True)
            return []

    async def get_routes_by_city(self, city_id: int) -> list[Route]:
        try:
            all_routes = await self.d_route_repo.get_list()
            d_route_ids = []
            for route in all_routes:
                if route.departure_city and route.destination_city and city_id in {route.departure_city.city_id, route.destination_city.city_id}:
                    d_route_ids.append(route.d_route_id)
                        
            routes = []
            async for doc in self.routes.find({"d_route._id": {"$in": d_route_ids}}):
                d_route_doc = await self.d_route_repo.get_by_id(doc["d_route"]["_id"])
                travel_doc = await self.travel_repo.get_by_id(doc["travel"]["_id"])
                
                routes.append(Route(
                    route_id=int(doc["_id"]),
                    d_route=d_route_doc,
                    travels=travel_doc,
                    start_time=doc["start_time"],
                    end_time=doc["end_time"],
                    type=doc["type"]
                ))
            
            logger.debug("Маршрут с city ID %d успешно найден", city_id)
            return routes
        except PyMongoError as e:
            logger.error("Ошибка при получении маршрута с city ID %d: %s", city_id, str(e), exc_info=True)
            return []

    async def delete_city_from_route(self, travel_id: int, city_id: int) -> None:
        try:
            routes = await self.get_routes_by_travel_id_ordered(travel_id)
            if not routes:
                raise ValueError("Маршрут пуст")

            segments_to_remove = []
            for i, route in enumerate(routes):
                if not route.d_route:
                    continue
                    
                if city_id in {
                    route.d_route.departure_city.city_id if route.d_route.departure_city else None,
                    route.d_route.destination_city.city_id if route.d_route.destination_city else None
                }:
                    segments_to_remove.append(i)

            if not segments_to_remove:
                raise ValueError(f"Город {city_id} не найден в маршруте")

            prev_city_id = None
            next_city_id = None
            
            first_segment_idx = segments_to_remove[0]
            if first_segment_idx > 0:
                prev_route = routes[first_segment_idx - 1]
                if prev_route.d_route and prev_route.d_route.departure_city:
                    prev_city_id = prev_route.d_route.departure_city.city_id
            
            last_segment_idx = segments_to_remove[-1]
            if last_segment_idx < len(routes) - 1:
                next_route = routes[last_segment_idx + 1]
                if next_route.d_route and next_route.d_route.destination_city:
                    next_city_id = next_route.d_route.destination_city.city_id

            for i in sorted(segments_to_remove, reverse=True):
                await self.delete(routes[i].route_id)

            if prev_city_id and next_city_id:
                first_removed_route = routes[segments_to_remove[0]]
                if not first_removed_route.d_route:
                    raise ValueError("Не удалось определить транспорт для нового сегмента")
                    
                transport = first_removed_route.d_route.type_transport
                start_time = first_removed_route.start_time
                
                d_route = await self._get_d_route_between(prev_city_id, next_city_id, transport)
                new_route = Route(
                    route_id=1,
                    d_route=d_route,
                    travels=routes[0].travels,
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=2),
                    type=routes[0].type
                )
                await self.add(new_route)
        except PyMongoError as e:
            logger.error("Ошибка при удалении города из маршрута: %s", str(e), exc_info=True)
            raise

    async def change_transport(self, d_route_id: int, route_id: int, new_transport: str) -> Route | None:
        try:
            route_doc = await self.routes.find_one({"_id": route_id})
            logger.debug("route_doc: %s", route_doc)
            if not route_doc:
                logger.error("Невозможно поменять транспорт, маршрут с ID %d не найден", route_id)
                return None

            old_d_route = await self.d_route_repo.get_by_id(d_route_id)
            if not old_d_route or not old_d_route.departure_city or not old_d_route.destination_city:
                logger.error("Справочник маршрута с ID %d не найден", d_route_id)
                return None

            new_d_route = await self.d_route_repo.get_by_cities(old_d_route.departure_city.city_id, 
                                                        old_d_route.destination_city.city_id, new_transport)
            if not new_d_route or not new_d_route.departure_city or not new_d_route.destination_city:
                logger.error("Справочник маршрута с транспортом %s не найден", new_transport)
                return None

            result = await self.routes.update_one(
                {"_id": route_id},
                {"$set": {"d_route": {
                    "_id": new_d_route.d_route_id,
                    "type_transport": new_d_route.type_transport,
                    "departure_city_id": new_d_route.departure_city.city_id,
                    "arrival_city_id": new_d_route.destination_city.city_id,
                    "price": new_d_route.cost,
                    "distance": new_d_route.distance}}}
            )
            
            if result.modified_count == 0:
                logger.error("Не удалось обновить маршрут")
                return None
                
            logger.debug("Транспорт %s в маршруте ID %d успешно обновлён", new_transport, route_id)
            return await self.get_by_id(route_id)
        except PyMongoError as e:
            logger.error("Ошибка при изменении транспорта маршрута с ID %d: %s", route_id, str(e), exc_info=True)
            raise
        
    async def _get_d_route_between(self, from_city_id: int, to_city_id: int, transport: str) -> DirectoryRoute:
        d_route_doc = await self.d_route_repo.get_by_cities(from_city_id, to_city_id, transport)
        
        if not d_route_doc:
            raise ValueError(f"Нет маршрута между городами {from_city_id} и {to_city_id}")
            
        return d_route_doc
        
    async def insert_city_after(self, travel_id: int, new_city_id: int, after_city_id: int, transport: str) -> None:
        try:
            routes = await self.get_routes_by_travel_id_ordered(travel_id)
            if not routes:
                raise ValueError("Маршрут пуст")

            target_route = None
            insert_after = False
            
            for route in routes:
                if not route.d_route:
                    continue
                    
                if route.d_route.destination_city and route.d_route.destination_city.city_id == after_city_id:
                    target_route = route
                    insert_after = True
                    break
                if route.d_route.departure_city and route.d_route.departure_city.city_id == after_city_id:
                    target_route = route
                    break

            if not target_route or not target_route.d_route:
                raise ValueError(f"Город {after_city_id} не найден в маршруте")

            if insert_after:
                d_route_new = await self._get_d_route_between(after_city_id, new_city_id, transport)
                
                new_route = Route(
                    route_id=1,
                    d_route=d_route_new, 
                    travels=target_route.travels,
                    start_time=target_route.end_time,
                    end_time=target_route.end_time + timedelta(hours=2),
                    type=target_route.type
                )
                await self.add(new_route)
            else:
                d_route_new = await self._get_d_route_between(new_city_id, after_city_id, transport)
                if not d_route_new.departure_city or not d_route_new.destination_city:
                    raise ValueError("Город d_route_new.departure_city/d_route_new.destination_city не найден")
                await self.routes.update_one(
                    {"_id": target_route.route_id},
                    {"$set": {
                        "d_route": {"_id": d_route_new.d_route_id,
                                    "type_transport": d_route_new.type_transport,
                                    "departure_city_id": d_route_new.departure_city.city_id,
                                    "arrival_city_id": d_route_new.destination_city.city_id,
                                    "price": d_route_new.cost,
                                    "distance": d_route_new.distance}},
                        "end_time": target_route.start_time + timedelta(hours=2)
                    }
                )
        except PyMongoError as e:
            logger.error("Ошибка при вставке города в маршрут: %s", str(e), exc_info=True)
            raise

    async def get_routes_by_user_and_status_and_type(self, user_id: int, status: str, type_route: str) -> list[Route]:
        try:
            travel_ids = [t.travel_id for t in await self.travel_repo.get_travels_for_user(user_id, status)]
            
            routes = []
            async for doc in self.routes.find({
                "travel._id": {"$in": travel_ids},
                "type": type_route
            }):
                d_route_doc = await self.d_route_repo.get_by_id(doc["d_route"]["_id"])
                travel_doc = await self.travel_repo.get_by_id(doc["travel"]["_id"])
                
                routes.append(Route(
                    route_id=int(doc["_id"]),
                    d_route=d_route_doc,
                    travels=travel_doc,
                    start_time=doc["start_time"],
                    end_time=doc["end_time"],
                    type=doc["type"]
                ))
            
            logger.debug("Найдено %d маршрутов для user_id=%d со статусом %s", len(routes), user_id, status)
            return routes
        except PyMongoError as e:
            logger.error("Ошибка при получении маршрутов по user_id=%d и статусу %s: %s",
                        user_id, status, str(e), exc_info=True)
            raise

    async def get_routes_by_type(self, type_route: str) -> list[Route]:
        try:
            routes = []
            async for doc in self.routes.find({"type": type_route}):
                d_route_doc = await self.d_route_repo.get_by_id(doc["d_route"]["_id"])
                travel_doc = await self.travel_repo.get_by_id(doc["travel"]["_id"])
                
                routes.append(Route(
                    route_id=int(doc["_id"]),
                    d_route=d_route_doc,
                    travels=travel_doc,
                    start_time=doc["start_time"],
                    end_time=doc["end_time"],
                    type=doc["type"]
                ))
            
            logger.debug("Найдено %d маршрутов с типом %s", len(routes), type_route)
            return routes
        except PyMongoError as e:
            logger.error("Ошибка при получении маршрутов с типом %s: %s", type_route, str(e), exc_info=True)
            return []

    async def get_route_parts(self, route_id: int) -> list[dict[str, Any]]:
        try:
            route_parts = []
            async for route_doc in self.routes.find({"_id": route_id}).sort("start_time"):
                logger.debug("route_doc %s/n", route_doc)
                d_route_doc = await self.d_route_repo.get_by_id(route_doc["d_route"]["_id"])
                if not d_route_doc:
                    continue
                
                route_parts.append({
                    "route_id": int(route_doc["_id"]),
                    "d_route_id": d_route_doc.d_route_id,
                    "departure_city": d_route_doc.departure_city,
                    "destination_city": d_route_doc.destination_city,
                    "transport": d_route_doc.type_transport,
                    "start_time": route_doc["start_time"],
                    "end_time": route_doc["end_time"],
                    "type": route_doc["type"], 
                    "price": d_route_doc.cost
                })
            
            logger.debug("Получено %d частей маршрута для route_id=%d", len(route_parts), route_id)
            return route_parts
            
        except PyMongoError as e:
            logger.error("Ошибка при получении частей маршрута для route_id=%d: %s", 
                    route_id, str(e), exc_info=True)
            raise