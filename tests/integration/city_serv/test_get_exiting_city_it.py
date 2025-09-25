from __future__ import annotations

import pytest

from services.city_service import CityService


@pytest.mark.asyncio
async def test_get_existing_city(city_service: CityService) -> None:
    city = await city_service.get_by_id(1)

    assert city is not None
    assert city.name == "Москва"
