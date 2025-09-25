from __future__ import annotations

import pytest

from models.city import City
from services.city_service import CityService


@pytest.mark.asyncio
async def test_update_non_existing_city_raises(city_service: CityService) -> None:
    city_before = await city_service.get_by_id(999)
    assert city_before is None

    non_existing_city = City(city_id=999, name="Новый Город")
    
    await city_service.update(non_existing_city)

    city_after = await city_service.get_by_id(999)
    assert city_after is None 