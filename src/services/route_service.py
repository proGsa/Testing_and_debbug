from __future__ import annotations

import logging

from typing import Any

from abstract_repository.iroute_repository import IRouteRepository
from abstract_service.route_service import IRouteService
from models.route import Route


logger = logging.getLogger(__name__)

Route.model_rebuild()


class RouteService(IRouteService):
    def __init__(self, repository: IRouteRepository) -> None:
        self.repository = repository
        logger.debug("RouteService инициализирован")

    async def get_by_id(self, route_id: int) -> Route | None:
        logger.debug("Получение маршрута по ID %d", route_id)
        return await self.repository.get_by_id(route_id)

    async def get_all_routes(self) -> list[Route]:
        logger.debug("Получение списка всех маршрутов")
        return await self.repository.get_list()

    async def add(self, route: Route) -> Route:
        try:
            logger.debug("Добавление маршрута с ID %d", route.route_id)
            route = await self.repository.add(route)
        except (Exception):
            logger.error("Маршрут c таким ID %d уже существует.", route.route_id)
            raise ValueError("Маршрут c таким ID уже существует.")
        return route

    async def update(self, updated_route: Route) -> Route:
        try:
            logger.debug("Обновление маршрута с ID %d", updated_route.route_id)
            await self.repository.update(updated_route)
        except (Exception):
            logger.error("Маршрут с ID %d не найден.", updated_route.route_id)
            raise ValueError("Маршрут не найден.")
        return updated_route

    async def delete(self, route_id: int) -> None:
        try:
            logger.debug("Удаление маршрута с ID %d", route_id)
            await self.repository.delete(route_id)
        except (Exception):
            logger.error("Маршрут с ID %d не найден.", route_id)
            raise ValueError("Маршрут не найден.")

    async def insert_city_after(self, travel_id: int, new_city_id: int, after_city_id: int, transport: str) -> None:
        try:
            logger.debug("Добавление %d города после города %d в путешествии %d", 
                        new_city_id, after_city_id, travel_id)
            await self.repository.insert_city_after(travel_id, new_city_id, after_city_id, transport)
        except (Exception):
            logger.error("Не удалось добавить город %d в маршрут", new_city_id)
            raise ValueError("Город не получилось добавить.")

    async def delete_city_from_route(self, travel_id: int, city_id: int) -> None:
        try:
            logger.debug("Удаление города %d из маршрута", city_id)
            await self.repository.delete_city_from_route(travel_id, city_id)
        except (Exception):
            logger.error("Не удалось удалить город %d из маршрута", city_id)
            raise ValueError("Город не получилось удалить из маршрута.")

    async def change_transport(self, d_route_id: int, route_id: int, new_transport: str) -> Route | None:
        try:
            logger.debug("Изменение транспорта в маршруте %d на %s", 
                        route_id, new_transport)
            return await self.repository.change_transport(d_route_id, route_id, new_transport)
        except (Exception):
            logger.error("Не удалось изменить транспорт в маршруте %d", route_id)
            raise ValueError("Город не получилось удалить из маршрута.")

    async def get_routes_by_user_and_status_and_type(self, user_id: int, status: str, type_route: str) -> list[Route]:
        logger.debug("Получение маршрута по user_id %d, status %s, type: %s", user_id, status, type_route)
        return await self.repository.get_routes_by_user_and_status_and_type(user_id, status, type_route)

    async def get_routes_by_type(self, type_route: str) -> list[Route]:
        logger.debug("Получение маршрута по type: %s", type_route)
        return await self.repository.get_routes_by_type(type_route)

    async def get_route_parts(self, route_id: int) -> list[dict[str, Any]]:
        return await self.repository.get_route_parts(route_id)