from __future__ import annotations

import pytest

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_delete_city_from_route_success(route_service: RouteService) -> None:
    await route_service.delete_city_from_route(1, 3)
    