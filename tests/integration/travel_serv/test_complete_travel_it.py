from __future__ import annotations

import pytest

from services.travel_service import TravelService


@pytest.mark.asyncio
async def test_complete_travel_success(travel_service: TravelService) -> None:
    await travel_service.complete(1)
    result = await travel_service.get_by_id(1)
    assert result is not None
    assert result.status == "Завершен"
