from __future__ import annotations

import pytest

from services.directory_route_service import DirectoryRouteService


@pytest.mark.asyncio
async def test_get_directory_route_by_id_not_found(
    d_route_service: DirectoryRouteService,
) -> None:
    result = await d_route_service.get_by_id(999)

    assert result is None
