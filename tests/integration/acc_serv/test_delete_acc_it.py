from __future__ import annotations

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from services.accommodation_service import AccommodationService


@pytest.mark.asyncio
async def test_delete_existing_accommodation(
    accommodation_service: AccommodationService, db_session: AsyncSession
) -> None:
    await accommodation_service.delete(1)
    deleted = await accommodation_service.get_by_id(1)
    assert deleted is None
