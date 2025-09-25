from __future__ import annotations

import pytest

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_delete_non_existing_route_raises(route_service: RouteService) -> None:
    await route_service.delete(999)
    res = await route_service.get_by_id(999)
    assert res is None
