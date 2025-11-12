from __future__ import annotations

import pytest

from services.accommodation_service import AccommodationService


TWO = 2


@pytest.mark.asyncio
async def test_get_all_accommodations_success(
    accommodation_service: AccommodationService,
) -> None:
    accommodations = await accommodation_service.get_list()

    assert len(accommodations) == TWO
    names = [acc.name for acc in accommodations]
    assert "ABC" in names
    assert "Four Seasons" in names
