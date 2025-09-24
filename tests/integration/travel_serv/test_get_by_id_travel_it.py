from __future__ import annotations

import pytest

from services.travel_service import TravelService


@pytest.mark.asyncio
async def test_get_by_id_success(travel_service: TravelService) -> None:
    result = await travel_service.get_by_id(1)
    assert result is not None
    assert result.travel_id == 1
    assert result.status == "В процессе"