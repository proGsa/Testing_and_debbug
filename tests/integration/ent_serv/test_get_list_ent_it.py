from __future__ import annotations

import pytest

from services.entertainment_service import EntertainmentService


TWO = 2


@pytest.mark.asyncio
async def test_get_all_entertainments_success(entertainment_service: EntertainmentService) -> None:
    entertainments = await entertainment_service.get_list()
    
    assert len(entertainments) == TWO
    names = [ent.event_name for ent in entertainments]
    assert "Концерт" in names
    assert "Выставка" in names
