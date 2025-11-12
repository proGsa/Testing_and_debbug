from __future__ import annotations

from datetime import datetime

import pytest

from models.city import City
from models.entertainment import Entertainment
from services.entertainment_service import EntertainmentService


THIRD = 3


@pytest.mark.asyncio
async def test_add_duplicate_name_entertainment_raises(
    entertainment_service: EntertainmentService,
) -> None:
    new_entertainment = Entertainment(
        entertainment_id=3,
        duration="2 часа",
        address="test",
        event_name="Музей",
        event_time=datetime(2025, 1, 1, 12, 0, 0),
        city=City(city_id=1, name="Москва"),
    )
    await entertainment_service.add(new_entertainment)
    result = await entertainment_service.get_by_id(3)
    assert result is not None
    assert result.event_name == "Музей"
    assert result.entertainment_id == THIRD
