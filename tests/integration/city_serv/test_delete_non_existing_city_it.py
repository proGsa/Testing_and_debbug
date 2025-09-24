from __future__ import annotations

import pytest

from services.city_service import CityService


@pytest.mark.asyncio
async def test_delete_non_existing_city_raises(city_service: CityService) -> None:
    await city_service.delete(999)

    city = await city_service.get_by_id(999)
    assert city is None
