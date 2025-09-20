from __future__ import annotations

import logging

from abstract_repository.icity_repository import ICityRepository
from abstract_service.city_service import ICityService
from models.city import City


logger = logging.getLogger(__name__)


class CityService(ICityService):
    def __init__(self, repository: ICityRepository) -> None:
        self.repository = repository
        logger.debug("CityService инициализирован")

    async def get_by_id(self, city_id: int) -> City | None:
        logger.debug("Получение города по ID %d", city_id)
        return await self.repository.get_by_id(city_id)

    async def get_all_cities(self) -> list[City]:
        logger.debug("Получение списка всех городов")
        return await self.repository.get_list() 

    async def add(self, city: City) -> City:
        try:
            logger.debug("Добавление города с ID %d", city.city_id)
            city = await self.repository.add(city)
        except (Exception):
            logger.error("Город c таким ID %d уже существует.", city.city_id)
            raise ValueError("Город c таким ID уже существует.")
        return city

    async def update(self, updated_city: City) -> City:
        try:
            logger.debug("Обновление города с ID %d", updated_city.city_id)
            await self.repository.update(updated_city)
        except (Exception):
            logger.error("Город с ID %d не найден.", updated_city.city_id)
            raise ValueError("Город не найден.")
        return updated_city

    async def delete(self, city_id: int) -> None:
        try:
            logger.debug("Удаление города с ID %d", city_id)
            await self.repository.delete(city_id)
        except (Exception):
            logger.error("Город с ID %d не найден.", city_id)
            raise ValueError("Город не найден.")
