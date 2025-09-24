from __future__ import annotations

import pytest

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_change_transport_success(route_service: RouteService) -> None:
    result = await route_service.change_transport(1, 2, "Поезд")
    
    assert result is not None