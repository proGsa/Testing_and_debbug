from __future__ import annotations

import re

from datetime import datetime

import pytest

from models.city import City
from models.entertainment import Entertainment
from services.entertainment_service import EntertainmentService


@pytest.mark.asyncio
async def test_add_duplicate_name_entertainment_raises(
    entertainment_service: EntertainmentService,
) -> None:
    existing_entertainment = Entertainment(
        entertainment_id=1,
        duration="4 часа",
        address="Главная площадь",
        event_name="Концерт",
        event_time=datetime(2025, 4, 10, 16, 0, 0),
        city=City(city_id=1, name="Москва"),
    )
    with pytest.raises(
        ValueError, match=re.escape("Развлечение c таким ID уже существует.")
    ):
        await entertainment_service.add(existing_entertainment)
