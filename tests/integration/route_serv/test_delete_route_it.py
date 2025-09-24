from __future__ import annotations

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from services.route_service import RouteService


@pytest.mark.asyncio
async def test_delete_route_success(route_service: RouteService, db_session: AsyncSession) -> None:
    await route_service.delete(1)
    
    route = await route_service.get_by_id(1)
    assert route is None