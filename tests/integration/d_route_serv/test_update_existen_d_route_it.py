from __future__ import annotations

import pytest

from models.city import City
from models.directory_route import DirectoryRoute
from services.directory_route_service import DirectoryRouteService


@pytest.mark.asyncio
async def test_update_non_existing_directory_route_raises(d_route_service: DirectoryRouteService) -> None:
    fake_route = DirectoryRoute(
            d_route_id=999,
            type_transport="Паром",
            departure_city=City(city_id=3, name="Санкт-Петербург"),
            destination_city=City(city_id=5, name="Екатеринбург"),
            distance=100,
            cost=50
        )

    await d_route_service.update(fake_route)
    result = await d_route_service.get_by_id(999)
    assert result is None
