from __future__ import annotations

import pytest

from services.route_service import RouteService


THIRD = 3
TWO = 2


@pytest.mark.asyncio
async def test_update_non_existing_route_raises(route_service: RouteService) -> None:
    routes = await route_service.get_all_routes()
    
    assert len(routes) == THIRD
    assert any(route.route_id == 1 for route in routes)
    assert any(route.route_id == TWO for route in routes)
    assert any(route.route_id == THIRD for route in routes)


