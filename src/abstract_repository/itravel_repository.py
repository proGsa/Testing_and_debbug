from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.travel import Travel
from models.user import User


class ITravelRepository(ABC):
    @abstractmethod
    async def get_list(self) -> list[Travel]:
        pass

    @abstractmethod
    async def get_by_id(self, travel_id: int) -> Travel | None:
        pass

    @abstractmethod
    async def add(self, travel: Travel) -> Travel:
        pass

    @abstractmethod
    async def update(self, update_travel: Travel) -> None:
        pass

    @abstractmethod
    async def delete(self, travel_id: int) -> None:
        pass

    @abstractmethod
    async def get_accommodations_by_travel(self, travel_id: int) -> list[Accommodation]:
        pass
    
    @abstractmethod
    async def get_users_by_travel(self, travel_id: int) -> list[User]:
        pass

    @abstractmethod
    async def get_entertainments_by_travel(self, travel_id: int) -> list[Entertainment]:
        pass

    @abstractmethod
    async def get_travel_by_route_id(self, route_id: int) -> Travel | None:
        pass
    
    @abstractmethod
    async def search(self, travel_dict: dict[str, Any]) -> list[Travel]:  
        pass

    @abstractmethod
    async def complete(self, travel_id: int) -> None:
        pass

    @abstractmethod
    async def link_entertainments(self, travel_id: int, entertainment_ids: list[int]) -> None:
        pass

    @abstractmethod
    async def link_accommodations(self, travel_id: int, accommodation_ids: list[int]) -> None:
        pass

    @abstractmethod
    async def get_travels_for_user(self, user_id: int, status: str) -> list[Travel]:
        pass

    @abstractmethod
    async def link_users(self, travel_id: int, user_ids: list[int]) -> None:
        pass