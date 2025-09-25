from __future__ import annotations

import re

from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from models.route import Route
from repository.route_repository import RouteRepository
from services.route_service import RouteService


pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_should_successfull_get_route_by_id() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 2, 12, 0, 0), type="Свои")
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.get_by_id = AsyncMock(return_value=route)

    service = RouteService(repo)
    result = await service.get_by_id(1)

    assert result == route
    repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_should_throw_exception_when_get_by_id_fails() -> None:
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.get_by_id = AsyncMock(side_effect=ValueError)

    service = RouteService(repo)
    with pytest.raises(ValueError):
        await service.get_by_id(123)


@pytest.mark.asyncio
async def test_should_successfull_get_all_routes() -> None:
    routes = [Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 3, 12, 0, 0), type="Свои")]
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.get_list = AsyncMock(return_value=routes)

    service = RouteService(repo)
    result = await service.get_all_routes()

    assert result == routes
    repo.get_list.assert_awaited_once()


@pytest.mark.asyncio
async def test_should_successfull_add_route() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 3, 12, 0, 0), type="Свои")
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.add = AsyncMock(return_value=route)

    service = RouteService(repo)
    result = await service.add(route)

    assert result == route
    repo.add.assert_awaited_once_with(route)


@pytest.mark.asyncio
async def test_should_throw_exception_at_add_duplicate() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 3, 12, 0, 0), type="Свои")
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.add = AsyncMock(side_effect=Exception)

    service = RouteService(repo)
    with pytest.raises(ValueError, match=re.escape("Маршрут c таким ID уже существует.")):
        await service.add(route)


@pytest.mark.asyncio
async def test_should_successfull_update_route() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 3, 12, 0, 0), type="Свои")
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.update = AsyncMock(return_value=None)

    service = RouteService(repo)
    result = await service.update(route)

    assert result == route
    repo.update.assert_awaited_once_with(route)


@pytest.mark.asyncio
async def test_should_throw_exception_at_update_not_existed() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 3, 12, 0, 0), type="Свои")
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.update = AsyncMock(side_effect=Exception)

    service = RouteService(repo)
    with pytest.raises(ValueError, match=re.escape("Маршрут не найден.")):
        await service.update(route)


@pytest.mark.asyncio
async def test_should_successfull_delete_route() -> None:
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.delete = AsyncMock(return_value=None)

    service = RouteService(repo)
    await service.delete(1)

    repo.delete.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_should_throw_exception_at_delete_not_existed() -> None:
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.delete = AsyncMock(side_effect=Exception)

    service = RouteService(repo)
    with pytest.raises(ValueError, match=re.escape("Маршрут не найден.")):
        await service.delete(1)


@pytest.mark.asyncio
async def test_should_successfull_insert_city_after() -> None:
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.insert_city_after = AsyncMock(return_value=None)

    service = RouteService(repo)
    await service.insert_city_after(1, 2, 3, "автобус")

    repo.insert_city_after.assert_awaited_once_with(1, 2, 3, "автобус")


@pytest.mark.asyncio
async def test_should_throw_exception_at_insert_city_after() -> None:
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.insert_city_after = AsyncMock(side_effect=Exception)

    service = RouteService(repo)
    with pytest.raises(ValueError, match=re.escape("Город не получилось добавить.")):
        await service.insert_city_after(1, 2, 3, "автобус")


@pytest.mark.asyncio
async def test_should_successfull_delete_city_from_route() -> None:
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.delete_city_from_route = AsyncMock(return_value=None)

    service = RouteService(repo)
    await service.delete_city_from_route(1, 2)

    repo.delete_city_from_route.assert_awaited_once_with(1, 2)


@pytest.mark.asyncio
async def test_should_throw_exception_at_delete_city_from_route() -> None:
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.delete_city_from_route = AsyncMock(side_effect=Exception)

    service = RouteService(repo)
    with pytest.raises(ValueError, match=re.escape("Город не получилось удалить из маршрута.")):
        await service.delete_city_from_route(1, 2)


@pytest.mark.asyncio
async def test_should_successfull_change_transport() -> None:
    route = Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 3, 12, 0, 0), type="Свои")
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.change_transport = AsyncMock(return_value=route)

    service = RouteService(repo)
    result = await service.change_transport(1, 1, "поезд")

    assert result == route
    repo.change_transport.assert_awaited_once_with(1, 1, "поезд")


@pytest.mark.asyncio
async def test_should_throw_exception_at_change_transport() -> None:
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.change_transport = AsyncMock(side_effect=Exception)

    service = RouteService(repo)
    with pytest.raises(ValueError, match=re.escape("Город не получилось удалить из маршрута.")):
        await service.change_transport(1, 1, "поезд")


@pytest.mark.asyncio
async def test_should_successfull_get_routes_by_user_and_status_and_type() -> None:
    routes = [Route(route_id=1, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 3, 12, 0, 0), type="Свои")]
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.get_routes_by_user_and_status_and_type = AsyncMock(return_value=routes)

    service = RouteService(repo)
    result = await service.get_routes_by_user_and_status_and_type(1, "active", "Свои")

    assert result == routes
    repo.get_routes_by_user_and_status_and_type.assert_awaited_once_with(1, "active", "Свои")


@pytest.mark.asyncio
async def test_should_successfull_get_routes_by_type() -> None:
    routes = [Route(route_id=2, d_route=None, travels=None, start_time=datetime(2025, 1, 1, 12, 0, 0), end_time=datetime(2025, 1, 3, 12, 0, 0), type="Свои")]
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.get_routes_by_type = AsyncMock(return_value=routes)

    service = RouteService(repo)
    result = await service.get_routes_by_type("Свои")

    assert result == routes
    repo.get_routes_by_type.assert_awaited_once_with("Свои")


@pytest.mark.asyncio
async def test_should_successfull_get_route_parts() -> None:
    parts = [{"city": "Москва"}]
    repo = Mock(spec=RouteRepository, autospec=True)
    repo.get_route_parts = AsyncMock(return_value=parts)

    service = RouteService(repo)
    result = await service.get_route_parts(1)

    assert result == parts
    repo.get_route_parts.assert_awaited_once_with(1)