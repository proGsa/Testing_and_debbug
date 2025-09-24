from __future__ import annotations

from datetime import datetime

import pytest

from models.city import City
from models.entertainment import Entertainment
from services.entertainment_service import EntertainmentService


@pytest.mark.asyncio
async def test_update_non_existing_entertainment_raises(entertainment_service: EntertainmentService) -> None:
    non_existing = Entertainment(
            entertainment_id=999,
            duration="2 часа",
            address="test",
            event_name="Музей",
            event_time=datetime(2025, 1, 1, 12, 0, 0),
            city=(City(city_id=1, name="Москва")),
        )
    
    await entertainment_service.update(non_existing)

    result = await entertainment_service.get_by_id(999)
    assert result is None

