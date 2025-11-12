from __future__ import annotations

import pytest

from services.travel_service import TravelService


@pytest.mark.asyncio
async def test_get_accommodations_by_travel_error(
    travel_service: TravelService,
) -> None:
    result = await travel_service.get_accommodations_by_travel(999)
    assert result == []
