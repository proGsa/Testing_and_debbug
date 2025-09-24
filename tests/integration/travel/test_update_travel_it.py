from __future__ import annotations

import pytest

from services.travel_service import TravelService


@pytest.mark.asyncio
async def test_update_travel_success(travel_service: TravelService) -> None:
    travel = await travel_service.get_by_id(1)
    assert travel is not None
    
    travel.status = "Обновленный статус"
    result = await travel_service.update(travel)
    assert result.status == "Обновленный статус"