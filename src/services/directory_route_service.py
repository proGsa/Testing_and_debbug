from __future__ import annotations

import logging

from abstract_repository.idirectory_route_repository import IDirectoryRouteRepository
from abstract_service.directory_route_service import IDirectoryRouteService
from models.directory_route import DirectoryRoute


logger = logging.getLogger(__name__)


class DirectoryRouteService(IDirectoryRouteService):
    def __init__(self, repository: IDirectoryRouteRepository) -> None:
        self.repository = repository
        logger.debug("DirectoryRouteService инициализирован")

    async def get_by_id(self, d_route_id: int) -> DirectoryRoute | None:
        logger.debug("Получение справочника маршрутов по ID %d", d_route_id)
        return await self.repository.get_by_id(d_route_id)

    async def get_list(self) -> list[DirectoryRoute]:
        logger.debug("Получение списка всех справочников маршрутов")
        return await self.repository.get_list()

    async def add(self, d_route: DirectoryRoute) -> DirectoryRoute:
        try:
            logger.debug("Добавление справочника маршрутов с ID %d", d_route.d_route_id)
            d_route = await self.repository.add(d_route)
        except Exception:
            logger.error(
                "Справочник маршрутов c таким ID %d уже существует.", d_route.d_route_id
            )
            raise ValueError("Справочник маршрутов c таким ID уже существует.")
        return d_route

    async def update(self, updated_d_route: DirectoryRoute) -> DirectoryRoute:
        try:
            logger.debug(
                "Обновление справочника маршрутов с ID %d", updated_d_route.d_route_id
            )
            await self.repository.update(updated_d_route)
        except Exception:
            logger.error(
                "Справочник маршрутов с ID %d не найден.", updated_d_route.d_route_id
            )
            raise ValueError("Справочник маршрутов не найден.")
        return updated_d_route

    async def delete(self, d_route_id: int) -> None:
        try:
            logger.debug("Удаление справочника маршрутов с ID %d", d_route_id)
            await self.repository.delete(d_route_id)
        except Exception:
            logger.error("Не удалось удалить справочник маршрутов с ID %d", d_route_id)
            raise ValueError("Справочник маршрутов не получилось удалить.")

    async def change_transport(
        self, d_route_id: int, new_transport: str
    ) -> DirectoryRoute | None:
        try:
            logger.debug(
                "Изменение транспорта в справочнике маршрутов %d на %s",
                d_route_id,
                new_transport,
            )
            return await self.repository.change_transport(d_route_id, new_transport)
        except Exception:
            logger.error(
                "Не удалось изменить транспорт в справочнике маршрутов %d", d_route_id
            )
            raise ValueError("Не получилось изменить транспорт.")

    async def get_by_cities(
        self, from_city_id: int, to_city_id: int, transport: str
    ) -> DirectoryRoute | None:
        try:
            logger.debug(
                "Удалось найти справочник маршрутов по городам %s и %s",
                from_city_id,
                to_city_id,
            )
            return await self.repository.get_by_cities(
                from_city_id, to_city_id, transport
            )
        except Exception:
            logger.error(
                "Не удалось найти справочник маршрутов по городам %s и %s",
                from_city_id,
                to_city_id,
            )
            raise ValueError("Справочник маршрутов не получилось удалить.")
