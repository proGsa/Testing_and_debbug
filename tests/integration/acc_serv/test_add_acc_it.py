from __future__ import annotations

from datetime import datetime

import pytest

from models.accommodation import Accommodation
from models.city import City
from services.accommodation_service import AccommodationService


THIRD = 3


@pytest.mark.asyncio
async def test_add_accommodation_success(
    accommodation_service: AccommodationService,
) -> None:
    new_accommodation = Accommodation(
        accommodation_id=3,
        price=15000,
        address="Улица Ленина, 10",
        name="Новый Отель",
        type="Отель",
        rating=5,
        check_in=datetime(2025, 3, 29, 12, 30, 0),
        check_out=datetime(2025, 4, 5, 18, 0, 0),
        city=City(city_id=1, name="Москва"),
    )

    await accommodation_service.add(new_accommodation)
    result = await accommodation_service.get_by_id(3)
    assert result is not None
    assert result.name == "Новый Отель"
    assert result.accommodation_id == THIRD
