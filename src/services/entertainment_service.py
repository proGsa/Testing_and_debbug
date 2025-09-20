from __future__ import annotations

import logging

from abstract_repository.ientertainment_repository import IEntertainmentRepository
from abstract_service.entertainment_service import IEntertainmentService
from models.entertainment import Entertainment


logger = logging.getLogger(__name__)


class EntertainmentService(IEntertainmentService):
    def __init__(self, repository: IEntertainmentRepository) -> None:
        self.repository = repository
        logger.debug("EntertainmentService инициализирован")

    async def get_by_id(self, entertainment_id: int) -> Entertainment | None:
        logger.debug("Получение развлечения по ID %d", entertainment_id)
        return await self.repository.get_by_id(entertainment_id)

    async def add(self, entertainment: Entertainment) -> Entertainment:
        try:
            logger.debug("Добавление развлечения с ID %d", entertainment.entertainment_id)
            entertainment = await self.repository.add(entertainment)
        except (Exception):
            logger.error("Развлечение c таким ID %d уже существует.", entertainment.entertainment_id)
            raise ValueError("Развлечение c таким ID уже существует.")
        return entertainment

    async def update(self, update_entertainment: Entertainment) -> Entertainment:
        try:
            logger.debug("Обновление развлечения с ID %d", update_entertainment.entertainment_id)
            await self.repository.update(update_entertainment)
        except (Exception):
            logger.error("Развлечение с ID %d не найдено.", update_entertainment.entertainment_id)
            raise ValueError("Развлечение не найдено.")
        return update_entertainment

    async def delete(self, entertainment_id: int) -> None:
        try:
            logger.debug("Удаление развлечения с ID %d", entertainment_id)
            await self.repository.delete(entertainment_id)
        except (Exception):
            logger.error("Развлечение с ID %d не найдено.", entertainment_id)
            raise ValueError("Развлечение не найдено.")

    async def get_list(self) -> list[Entertainment]:
        logger.debug("Получение списка всех развлечений")
        return await self.repository.get_list()
