from __future__ import annotations

from datetime import datetime

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from models.city import City
from models.entertainment import Entertainment
from services.entertainment_service import EntertainmentService


@pytest.mark.asyncio
async def test_update_existing_entertainment(entertainment_service: EntertainmentService, db_session: AsyncSession) -> None:
    updated = Entertainment(
            entertainment_id=1,
            duration="2 часа",
            address="test",
            event_name="Музей",
            event_time=datetime(2025, 1, 1, 12, 0, 0),
            city=(City(city_id=1, name="Москва")),
        )
    
    result = await entertainment_service.update(updated)

    assert result is not None
    assert result.event_name == "Музей"
    assert result.entertainment_id == 1

