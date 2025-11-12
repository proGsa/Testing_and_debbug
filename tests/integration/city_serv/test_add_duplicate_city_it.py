from __future__ import annotations

import re

import pytest

from models.city import City
from services.city_service import CityService


@pytest.mark.asyncio
async def test_add_duplicate_city_raises(city_service: CityService) -> None:
    city = City(city_id=1, name="Москва")
    with pytest.raises(ValueError, match=re.escape("Город c таким ID уже существует.")):
        await city_service.add(city)
