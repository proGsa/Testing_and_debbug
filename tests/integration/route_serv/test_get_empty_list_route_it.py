from __future__ import annotations

import pytest

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_get_empty_routes(route_service: RouteService) -> None:
    for i in range(1, 4):
        await route_service.delete(i)
    routes = await route_service.get_all_routes()
    
    assert len(routes) == 0
