from __future__ import annotations

import pytest

from services.directory_route_service import DirectoryRouteService


@pytest.mark.asyncio
async def test_update_directory_route_success(d_route_service: DirectoryRouteService) -> None:
    route = await d_route_service.get_by_id(2)
    assert route is not None

    route.type_transport = "Поезд"
    await d_route_service.update(route)

    updated = await d_route_service.get_by_id(2)
    assert updated is not None
    assert updated.type_transport == "Поезд"