from __future__ import annotations

import pytest

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_insert_city_after_success(route_service: RouteService) -> None:
    await route_service.insert_city_after(1, 4, 5, "Поезд")
    
