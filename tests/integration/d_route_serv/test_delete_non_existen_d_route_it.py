from __future__ import annotations

import pytest

from services.directory_route_service import DirectoryRouteService


@pytest.mark.asyncio
async def test_delete_non_existing_directory_route_raises(d_route_service: DirectoryRouteService) -> None:
    await d_route_service.delete(999)

    d_route = await d_route_service.get_by_id(999)
    assert d_route is None