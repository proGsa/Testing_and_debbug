from __future__ import annotations

import pytest

from services.travel_service import TravelService


@pytest.mark.asyncio
async def test_search_travels_success(travel_service: TravelService) -> None:
    result = await travel_service.search({"departure_city": 3})
    assert len(result) == 1
    assert result is not None
    assert result[0].travel_id == 1
