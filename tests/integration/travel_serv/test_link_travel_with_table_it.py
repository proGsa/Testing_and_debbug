from __future__ import annotations

import pytest

from services.travel_service import TravelService


TWO = 2


@pytest.mark.asyncio
async def test_link_entertainments_success(travel_service: TravelService) -> None:
    await travel_service.link_entertainments(1, [1, 2])
    result = await travel_service.get_entertainments_by_travel(1)
    assert len(result) == TWO
