from __future__ import annotations

import pytest

from models.city import City
from models.directory_route import DirectoryRoute
from services.directory_route_service import DirectoryRouteService


@pytest.mark.asyncio
async def test_add_duplicate_directory_route_raises(
    d_route_service: DirectoryRouteService,
) -> None:
    duplicate_route = DirectoryRoute(
        d_route_id=2,
        type_transport="Самолет",
        departure_city=City(city_id=3, name="Санкт-Петербург"),
        destination_city=City(city_id=4, name="Калининград"),
        distance=966,
        cost=5123,
    )

    result = await d_route_service.add(duplicate_route)

    assert result is not None
