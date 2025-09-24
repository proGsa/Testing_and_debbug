from __future__ import annotations

import pytest

from services.directory_route_service import DirectoryRouteService


@pytest.mark.asyncio
async def test_get_directory_route_by_id_success(d_route_service: DirectoryRouteService) -> None:
    d_route = await d_route_service.get_by_id(1)

    assert d_route is not None
    assert d_route.d_route_id == 1
    assert d_route.type_transport in {"Паром", "Самолет", "Автобус"}

