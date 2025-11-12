from __future__ import annotations

import pytest

from services.accommodation_service import AccommodationService


@pytest.mark.asyncio
async def test_get_accommodation_by_id_success(
    accommodation_service: AccommodationService,
) -> None:
    accommodation = await accommodation_service.get_by_id(1)

    assert accommodation is not None
    assert accommodation.name == "ABC"
    assert accommodation.accommodation_id == 1
