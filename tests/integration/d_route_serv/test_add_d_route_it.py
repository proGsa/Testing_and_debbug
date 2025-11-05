from __future__ import annotations

import pytest

from models.city import City
from models.directory_route import DirectoryRoute
from services.directory_route_service import DirectoryRouteService


FOUR = 13

@pytest.mark.asyncio
async def test_add_directory_route_success(d_route_service: DirectoryRouteService) -> None:
    new_route = DirectoryRoute(
            d_route_id=13,
            type_transport="Поезд",
            departure_city=City(city_id=1, name="Москва"),
            destination_city=City(city_id=5, name="Екатеринбург"),
            distance=600,
            cost=2000
        )
        
    result = await d_route_service.add(new_route)

    assert result.d_route_id == FOUR
    assert result.type_transport == "Поезд"
