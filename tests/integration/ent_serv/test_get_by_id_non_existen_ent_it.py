from __future__ import annotations

import pytest

from services.entertainment_service import EntertainmentService


@pytest.mark.asyncio
async def test_get_entertainment_by_id_not_found(entertainment_service: EntertainmentService) -> None:
    entertainment = await entertainment_service.get_by_id(999)
    
    assert entertainment is None
