from __future__ import annotations

import pytest

from services.entertainment_service import EntertainmentService


@pytest.mark.asyncio
async def test_get_entertainment_by_id_success(
    entertainment_service: EntertainmentService,
) -> None:
    entertainment = await entertainment_service.get_by_id(1)

    assert entertainment is not None
    assert entertainment.event_name == "Концерт"
    assert entertainment.entertainment_id == 1
