from __future__ import annotations

import pytest

from models.city import City
from services.city_service import CityService


@pytest.mark.asyncio
async def test_add_city_success(city_service: CityService) -> None:
    new_city = City(city_id=6, name="Рязань")
    
    result = await city_service.add(new_city)
    
    assert result.name == "Рязань"

    city_in_db = await city_service.get_by_id(6)
    assert city_in_db is not None
    assert city_in_db.name == "Рязань"