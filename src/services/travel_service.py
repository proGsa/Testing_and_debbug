from __future__ import annotations

import logging

from typing import Any

from abstract_repository.itravel_repository import ITravelRepository
from abstract_service.travel_service import ITravelService
from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.travel import Travel
from models.user import User


logger = logging.getLogger(__name__)

Travel.model_rebuild()


class TravelService(ITravelService):
    def __init__(self, repository: ITravelRepository) -> None:
        self.repository = repository
        logger.debug("TravelService инициализирован")

    async def get_by_id(self, travel_id: int) -> Travel | None:
        logger.debug("Получение путешествия по ID %d", travel_id)
        return await self.repository.get_by_id(travel_id)

    async def get_all_travels(self) -> list[Travel]:
        logger.debug("Получение списка всех путешествий")
        return await self.repository.get_list() 

    async def add(self, travel: Travel) -> Travel:
        try:
            logger.debug("Добавление путешествия с ID %d", travel.travel_id)
            travel = await self.repository.add(travel)
        except (Exception):
            logger.error("Путешествие c таким ID %d уже существует.", travel.travel_id)
            raise ValueError("Путешествие c таким ID уже существует.")
        return travel

    async def update(self, update_travel: Travel) -> Travel:
        try:
            logger.debug("Обновление путешествия с ID %d", update_travel.travel_id)
            await self.repository.update(update_travel)
        except (Exception):
            logger.error("Путешествие с ID %d не найдено.", update_travel.travel_id)
            raise ValueError("Путешествие не найдено.")
        return update_travel

    async def delete(self, travel_id: int) -> None:
        try:
            logger.debug("Удаление путешествия с ID %d", travel_id)
            await self.repository.delete(travel_id)
        except (Exception):
            logger.error("Путешествие с ID %d не найдено.", travel_id)
            raise ValueError("Путешествие не найдено.")

    async def search(self, travel_dict: dict[str, Any]) -> list[Travel]:
        try:
            logger.debug("Поиск путешествий по параметрам: %s", travel_dict)
            return await self.repository.search(travel_dict)
        except (Exception):
            logger.error("Путешествия по параметрам %s не найдены", travel_dict)
            raise ValueError("Путешествие по переданным параметрам не найдено.")
    
    async def complete(self, travel_id: int) -> None:
        try:
            logger.debug("Завершение путешествия с ID %d", travel_id)
            await self.repository.complete(travel_id)
        except (Exception):
            logger.error("Ошибка при завершении путешествия %d", travel_id)
            raise ValueError("Ошибка при завершении путешествия")

    async def get_users_by_travel(self, travel_id: int) -> list[User]:
        try:
            logger.debug("Получение пользователей для путешествия %d", travel_id)
            return await self.repository.get_users_by_travel(travel_id)
        except (Exception):
            logger.error("Ошибка при получении пользователей для путешествия %d", travel_id)
            raise ValueError("Ошибка при получении пользователей")

    async def get_entertainments_by_travel(self, travel_id: int) -> list[Entertainment]:
        try:
            logger.debug("Получение развлечений для путешествия %d", travel_id)
            return await self.repository.get_entertainments_by_travel(travel_id)
        except (Exception):
            logger.error("Ошибка при получении развлечений для путешествия %d", travel_id)
            raise ValueError("Ошибка при получении развлечений для путешествий")

    async def get_accommodations_by_travel(self, travel_id: int) -> list[Accommodation]:
        try:
            logger.debug("Получение мест проживания для путешествия %d", travel_id)
            return await self.repository.get_accommodations_by_travel(travel_id)
        except (Exception):
            logger.error("Ошибка при получении мест проживания для путешествия %d", travel_id)
            raise ValueError("Ошибка при получении завершенных путешествий")

    async def link_entertainments(self, travel_id: int, entertainment_ids: list[int]) -> None:
        try:
            logger.debug("Связывание развлечений %s с путешествием %d", entertainment_ids, travel_id)
            await self.repository.link_entertainments(travel_id, entertainment_ids)
        except Exception:
            logger.error("Ошибка при связывании развлечений %s с путешествием %d", entertainment_ids, travel_id)
            raise ValueError("Ошибка при связывании развлечений с путешествием.")

    async def link_users(self, travel_id: int, user_ids: list[int]) -> None:
        try:
            logger.debug("Связывание пользователей %s с путешествием %d", user_ids, travel_id)
            await self.repository.link_users(travel_id, user_ids)
        except Exception:
            logger.error("Ошибка при связывании пользователей %s с путешествием %d", user_ids, travel_id)
            raise ValueError("Ошибка при связывании пользователей с путешествием.")

    async def link_accommodations(self, travel_id: int, accommodation_ids: list[int]) -> None:
        try:
            logger.debug("Связывание мест проживания %s с путешествием %d", accommodation_ids, travel_id)
            await self.repository.link_accommodations(travel_id, accommodation_ids)
        except Exception:
            logger.error("Ошибка при связывании мест проживания %s с путешествием %d", accommodation_ids, travel_id)
            raise ValueError("Ошибка при связывании мест проживания с путешествием.")

    async def get_travels_for_user(self, user_id: int, travel_status: str) -> list[Travel]:
        try:
            logger.debug("Получение активных путешествий")
            return await self.repository.get_travels_for_user(user_id, travel_status)
        except (Exception):
            logger.error("Ошибка при получении активных путешествий")
            raise ValueError("Ошибка при получении активных путешествий")

    async def get_travel_by_route_id(self, route_id: int) -> Travel | None:
        try:
            logger.debug("Получение  путешествий по route ID %d", route_id)
            return await self.repository.get_travel_by_route_id(route_id)
        except (Exception):
            logger.error("Путешествие по route ID %d не найдено", route_id)
            raise ValueError("Ошибка при получении путешествий по route ID %d", route_id)
    