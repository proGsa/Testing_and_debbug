from __future__ import annotations

import pytest

from services.entertainment_service import EntertainmentService


@pytest.mark.asyncio
async def test_get_empty_list_entertainments(
    entertainment_service: EntertainmentService,
) -> None:
    await entertainment_service.delete(1)
    await entertainment_service.delete(2)
    entertainments = await entertainment_service.get_list()

    assert len(entertainments) == 0
