from __future__ import annotations

import pytest

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_get_route_by_id_not_found(route_service: RouteService) -> None:
    route = await route_service.get_by_id(999)

    assert route is None
