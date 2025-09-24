from __future__ import annotations

import pytest

from services.city_service import CityService


@pytest.mark.asyncio
async def test_get_non_existing_city_returns_none(city_service: CityService) -> None:
    city = await city_service.get_by_id(999)
    assert city is None