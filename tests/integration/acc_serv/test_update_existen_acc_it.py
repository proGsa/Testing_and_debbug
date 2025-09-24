from __future__ import annotations

from datetime import datetime

import pytest

from models.accommodation import Accommodation
from models.city import City
from services.accommodation_service import AccommodationService


@pytest.mark.asyncio
async def test_update_existing_accommodation(accommodation_service: AccommodationService) -> None:
    updated = Accommodation(
            accommodation_id=1,
            price=20000,
            address="ул. Пушкина, 5",
            name="Обновленный отель",
            type="Отель",
            rating=5,
            check_in=datetime(2025, 3, 29, 12, 30, 0),
            check_out=datetime(2025, 4, 5, 18, 0, 0),
            city=City(city_id=2, name="Воронеж")
        )
    
    result = await accommodation_service.update(updated)

    assert result is not None
    assert result.name == "Обновленный отель"
