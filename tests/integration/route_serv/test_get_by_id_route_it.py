from __future__ import annotations

import pytest

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_get_route_by_id_success(route_service: RouteService) -> None:
    route = await route_service.get_by_id(1)
    
    assert route is not None
    assert route.route_id == 1
    assert route.type == "Свои"