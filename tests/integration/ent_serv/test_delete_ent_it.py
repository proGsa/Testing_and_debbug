from __future__ import annotations

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from services.entertainment_service import EntertainmentService


@pytest.mark.asyncio
async def test_delete_existing_entertainment(
    entertainment_service: EntertainmentService, db_session: AsyncSession
) -> None:
    await entertainment_service.delete(1)
    deleted = await entertainment_service.get_by_id(1)
    assert deleted is None
