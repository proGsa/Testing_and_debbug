from __future__ import annotations

import logging

from abstract_repository.iaccommodation_repository import IAccommodationRepository
from abstract_service.accommodation_service import IAccommodationService
from models.accommodation import Accommodation


logger = logging.getLogger(__name__)


class AccommodationService(IAccommodationService):
    def __init__(self, repository: IAccommodationRepository) -> None:
        self.repository = repository
        logger.debug("AccommodationService инициализирован")

    async def get_by_id(self, accommodation_id: int) -> Accommodation | None:
        logger.debug("Получение размещения по ID %d", accommodation_id)
        return await self.repository.get_by_id(accommodation_id)

    async def get_list(self) -> list[Accommodation]:
        logger.debug("Получение списка размещений")
        return await self.repository.get_list()

    async def add(self, accommodation: Accommodation) -> Accommodation:
        try:
            logger.debug("Добавления размещения с ID %d", accommodation.accommodation_id)
            accommodation = await self.repository.add(accommodation)
        except (Exception):
            logger.error("Размещение c таким ID %d уже существует.", accommodation.accommodation_id)
            raise ValueError("Размещение c таким ID уже существует.")
        return accommodation

    async def update(self, update_accommodation: Accommodation) -> Accommodation:
        try:
            logger.debug("Обновление размещения с ID %d", update_accommodation.accommodation_id)
            await self.repository.update(update_accommodation)
        except (Exception):
            logger.error("Размещение c таким ID %d не найдено.", update_accommodation.accommodation_id)
            raise ValueError("Размещение c таким ID не найдено.")
        return update_accommodation

    async def delete(self, accommodation_id: int) -> None:
        try:
            logger.debug("Размещение с ID %d успешно удалено", accommodation_id)
            await self.repository.delete(accommodation_id)
        except (Exception):
            logger.error("Размещение c таким ID %d не найдено.", accommodation_id)
            raise ValueError("Размещение не найдено.")


