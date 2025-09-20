from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from models.route import Route


class IRouteRepository(ABC):
    @abstractmethod
    async def get_list(self) -> list[Route]:
        pass

    @abstractmethod
    async def get_by_id(self, route_id: int) -> Route | None:
        pass

    @abstractmethod
    async def add(self, route: Route) -> Route:
        pass

    @abstractmethod
    async def update(self, update_route: Route) -> None:
        pass

    @abstractmethod
    async def delete(self, route_id: int) -> None:
        pass
    
    @abstractmethod
    async def get_routes_by_travel_id_ordered(self, travel_id: int) -> list[Route]:
        pass

    @abstractmethod
    async def get_routes_by_city(self, city_id: int) -> list[Route]:
        pass

    @abstractmethod
    async def delete_city_from_route(self, travel_id: int, city_id: int) -> None:
        pass

    @abstractmethod
    async def change_transport(self, d_route_id: int, route_id: int, new_transport: str) -> Route | None:
        pass

    @abstractmethod
    async def insert_city_after(self, travel_id: int, new_city_id: int, after_city_id: int, transport: str) -> None:
        pass

    @abstractmethod
    async def get_routes_by_user_and_status_and_type(self, user_id: int, status: str, type_route: str) -> list[Route]:
        pass
    
    @abstractmethod
    async def get_routes_by_type(self, type_route: str) -> list[Route]:
        pass

    @abstractmethod
    async def get_route_parts(self, travel_id: int) -> list[dict[str, Any]]:
        pass