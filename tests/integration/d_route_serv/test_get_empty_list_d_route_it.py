from __future__ import annotations

import pytest

from services.directory_route_service import DirectoryRouteService


@pytest.mark.asyncio
async def test_get_empty_list(d_route_service: DirectoryRouteService) -> None:
    for i in range(1, 13):
        await d_route_service.delete(i)
    routes = await d_route_service.get_list()

    assert len(routes) == 0