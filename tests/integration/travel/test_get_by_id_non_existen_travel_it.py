from __future__ import annotations

import pytest

from services.travel_service import TravelService


@pytest.mark.asyncio
async def test_get_by_id_not_found(travel_service: TravelService) -> None:
    result = await travel_service.get_by_id(999)
    assert result is None