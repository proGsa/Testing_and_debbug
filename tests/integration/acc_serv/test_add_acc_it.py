from __future__ import annotations

import re

from datetime import datetime

import pytest

from models.accommodation import Accommodation
from models.city import City
from services.accommodation_service import AccommodationService


@pytest.mark.asyncio
async def test_add_duplicate_name_accommodation_raises(accommodation_service: AccommodationService) -> None:
    existing_accommodation = Accommodation(
            accommodation_id=2,
            price=33450,
            address="ул. Дмитриевского, 7",
            name="ABC",
            type="Квартира",
            rating=3,
            check_in=datetime(2025, 4, 2, 14, 0, 0),
            check_out=datetime(2025, 4, 6, 18, 0, 0),
            city=City(city_id=1, name="Москва")
        )
    with pytest.raises(ValueError, match=re.escape("Размещение c таким ID уже существует.")):
        await accommodation_service.add(existing_accommodation)
