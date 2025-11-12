from __future__ import annotations

import pytest

from services.travel_service import TravelService


@pytest.mark.asyncio
async def test_get_empty_list(travel_service: TravelService) -> None:
    await travel_service.delete(1)
    await travel_service.delete(2)
    result = await travel_service.get_all_travels()
    assert len(result) == 0
