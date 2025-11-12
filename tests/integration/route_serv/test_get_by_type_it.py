from __future__ import annotations

import pytest

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_get_routes_by_type_success(route_service: RouteService) -> None:
    routes = await route_service.get_routes_by_type("Свои")

    assert len(routes) > 0
    assert all(route.type == "Свои" for route in routes)
