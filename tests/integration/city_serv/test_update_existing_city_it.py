from __future__ import annotations

import pytest

from models.city import City
from services.city_service import CityService


@pytest.mark.asyncio
async def test_update_existing_city(city_service: CityService) -> None:
    updated_city = City(city_id=1, name="Адлер")
    result = await city_service.update(updated_city)

    assert result.name == "Адлер"

    city_in_db = await city_service.get_by_id(1)
    assert city_in_db is not None
    assert city_in_db.name == "Адлер"
