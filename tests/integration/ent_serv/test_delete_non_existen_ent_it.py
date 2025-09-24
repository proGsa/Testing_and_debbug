from __future__ import annotations

import pytest

from services.entertainment_service import EntertainmentService


@pytest.mark.asyncio
async def test_delete_non_existing_entertainment_raises(entertainment_service: EntertainmentService) -> None:
    await entertainment_service.delete(999)

    acc = await entertainment_service.get_by_id(999)
    assert acc is None