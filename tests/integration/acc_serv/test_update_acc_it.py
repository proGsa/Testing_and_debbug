from __future__ import annotations

from datetime import datetime

import pytest

from models.accommodation import Accommodation
from models.city import City
from services.accommodation_service import AccommodationService


@pytest.mark.asyncio
async def test_update_accommodation_raises(accommodation_service: AccommodationService) -> None:
    non_existing = Accommodation(
            accommodation_id=999,
            price=1000,
            address="Улица Ленина, 10",
            name="Несуществующее размещение",
            type="Отель",
            rating=5,
            check_in=datetime(2025, 3, 29, 12, 30, 0),
            check_out=datetime(2025, 4, 5, 18, 0, 0),
            city=City(city_id=1, name="Москва")
        )

    await accommodation_service.update(non_existing)

    result = await accommodation_service.get_by_id(999)
    assert result is None

