from __future__ import annotations

import pytest

from services.city_service import CityService


@pytest.mark.asyncio
async def test_get_all_cities_empty_list(city_service: CityService) -> None:
    for i in range(1, 6):
        await city_service.delete(i)
    cities = await city_service.get_all_cities()

    assert len(cities) == 0
