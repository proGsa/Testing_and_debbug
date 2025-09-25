from __future__ import annotations

import pytest

from services.city_service import CityService


TMP = 5


@pytest.mark.asyncio
async def test_get_all_cities_success(city_service: CityService) -> None:
    cities = await city_service.get_all_cities()

    assert cities is not None
    assert len(cities) == TMP