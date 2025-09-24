from __future__ import annotations

import pytest

from services.city_service import CityService


@pytest.mark.asyncio
async def test_delete_existing_city(city_service: CityService) -> None:
    await city_service.delete(1)
    city_in_db = await city_service.get_by_id(1)
    assert city_in_db is None
