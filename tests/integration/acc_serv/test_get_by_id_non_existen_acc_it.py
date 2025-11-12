from __future__ import annotations

import pytest

from services.accommodation_service import AccommodationService


@pytest.mark.asyncio
async def test_get_accommodation_by_id_not_found(
    accommodation_service: AccommodationService,
) -> None:
    accommodation = await accommodation_service.get_by_id(999)

    assert accommodation is None
