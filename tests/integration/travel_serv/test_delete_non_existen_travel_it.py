from __future__ import annotations

import pytest

from services.travel_service import TravelService


@pytest.mark.asyncio
async def test_delete_travel_not_found(travel_service: TravelService) -> None:
    await travel_service.delete(999) 
    result = await travel_service.get_by_id(999)
    assert result is None