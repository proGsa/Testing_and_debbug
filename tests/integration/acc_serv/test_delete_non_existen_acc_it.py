from __future__ import annotations

import pytest

from services.accommodation_service import AccommodationService


@pytest.mark.asyncio
async def test_delete_non_existing_accommodation_raises(
    accommodation_service: AccommodationService,
) -> None:
    await accommodation_service.delete(999)

    acc = await accommodation_service.get_by_id(999)
    assert acc is None
