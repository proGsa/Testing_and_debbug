from __future__ import annotations

import pytest

from services.directory_route_service import DirectoryRouteService


@pytest.mark.asyncio
async def test_delete_directory_route_success(
    d_route_service: DirectoryRouteService,
) -> None:
    await d_route_service.delete(3)

    deleted = await d_route_service.get_by_id(3)
    assert deleted is None
