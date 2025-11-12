from __future__ import annotations

import pytest

from services.accommodation_service import AccommodationService


@pytest.mark.asyncio
async def test_get_empty_list_accommodations(
    accommodation_service: AccommodationService,
) -> None:
    await accommodation_service.delete(1)
    await accommodation_service.delete(2)
    accommodations = await accommodation_service.get_list()

    assert len(accommodations) == 0
