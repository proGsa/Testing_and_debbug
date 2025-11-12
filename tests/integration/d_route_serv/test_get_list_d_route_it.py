from __future__ import annotations

import pytest

from services.directory_route_service import DirectoryRouteService


TMP = 12


@pytest.mark.asyncio
async def test_get_list_directory_routes(
    d_route_service: DirectoryRouteService,
) -> None:
    routes = await d_route_service.get_list()

    assert len(routes) == TMP
    names = [r.type_transport for r in routes]
    assert "Паром" in names
    assert "Самолет" in names
    assert "Автобус" in names
