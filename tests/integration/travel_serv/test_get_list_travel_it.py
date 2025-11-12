from __future__ import annotations

import pytest

from services.travel_service import TravelService


TWO = 2


@pytest.mark.asyncio
async def test_get_all_travels_success(travel_service: TravelService) -> None:
    result = await travel_service.get_all_travels()
    assert len(result) == TWO
    assert result[0].travel_id == 1
    assert result[1].travel_id == TWO
