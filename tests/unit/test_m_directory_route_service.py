from __future__ import annotations

import re

from unittest.mock import Mock

import pytest

from models.directory_route import DirectoryRoute
from services.directory_route_service import DirectoryRouteService


pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_should_successfull_get_existed_d_route_by_id(mock_repo: Mock) -> None:
    d_route = DirectoryRoute(
        d_route_id=1,
        type_transport="Самолет",
        cost=25866,
        distance=300000,
        departure_city=None,
        destination_city=None,
    )
    mock_repo.get_by_id.return_value = d_route
    service = DirectoryRouteService(mock_repo)

    result = await service.get_by_id(1)

    assert result == d_route
    mock_repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_get_not_existed_d_route(
    mock_repo: Mock,
) -> None:
    mock_repo.get_by_id.side_effect = ValueError("Not found")
    service = DirectoryRouteService(mock_repo)

    with pytest.raises(ValueError):
        await service.get_by_id(123)


@pytest.mark.asyncio
async def test_should_successfull_get_list(mock_repo: Mock) -> None:
    d_routes = [
        DirectoryRoute(
            d_route_id=1,
            type_transport="Самолет",
            cost=100,
            distance=200,
            departure_city=None,
            destination_city=None,
        ),
        DirectoryRoute(
            d_route_id=2,
            type_transport="Поезд",
            cost=50,
            distance=300,
            departure_city=None,
            destination_city=None,
        ),
    ]
    mock_repo.get_list.return_value = d_routes
    service = DirectoryRouteService(mock_repo)

    result = await service.get_list()

    assert result == d_routes
    mock_repo.get_list.assert_awaited_once()


@pytest.mark.asyncio
async def test_should_successfull_add_d_route(mock_repo: Mock) -> None:
    d_route = DirectoryRoute(
        d_route_id=1,
        type_transport="Автобус",
        cost=200,
        distance=150,
        departure_city=None,
        destination_city=None,
    )
    mock_repo.add.return_value = d_route
    service = DirectoryRouteService(mock_repo)

    result = await service.add(d_route)

    assert result == d_route
    mock_repo.add.assert_awaited_once_with(d_route)


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_add_duplicate_d_route(
    mock_repo: Mock,
) -> None:
    d_route = DirectoryRoute(
        d_route_id=1,
        type_transport="Автобус",
        cost=200,
        distance=150,
        departure_city=None,
        destination_city=None,
    )
    mock_repo.add.side_effect = Exception("Duplicate")
    service = DirectoryRouteService(mock_repo)

    with pytest.raises(
        ValueError, match=re.escape("Справочник маршрутов c таким ID уже существует.")
    ):
        await service.add(d_route)


@pytest.mark.asyncio
async def test_should_successfull_update_existed_d_route_by_id(mock_repo: Mock) -> None:
    d_route = DirectoryRoute(
        d_route_id=1,
        type_transport="Самолет",
        cost=25866,
        distance=300000,
        departure_city=None,
        destination_city=None,
    )
    service = DirectoryRouteService(mock_repo)

    result = await service.update(d_route)

    assert result == d_route
    mock_repo.update.assert_awaited_once_with(d_route)


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_update_not_existed_d_route(
    mock_repo: Mock,
) -> None:
    d_route = DirectoryRoute(
        d_route_id=1,
        type_transport="Самолет",
        cost=25866,
        distance=300000,
        departure_city=None,
        destination_city=None,
    )
    mock_repo.update.side_effect = Exception("Not found")
    service = DirectoryRouteService(mock_repo)

    with pytest.raises(ValueError, match=re.escape("Справочник маршрутов не найден.")):
        await service.update(d_route)


@pytest.mark.asyncio
async def test_should_successfull_delete_existed_d_route(mock_repo: Mock) -> None:
    service = DirectoryRouteService(mock_repo)

    await service.delete(123)

    mock_repo.delete.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_delete_not_existed_d_route(
    mock_repo: Mock,
) -> None:
    mock_repo.delete.side_effect = Exception("Not found")
    service = DirectoryRouteService(mock_repo)

    with pytest.raises(
        ValueError, match=re.escape("Справочник маршрутов не получилось удалить.")
    ):
        await service.delete(123)


@pytest.mark.asyncio
async def test_should_successfull_change_transport(mock_repo: Mock) -> None:
    d_route = DirectoryRoute(
        d_route_id=1,
        type_transport="Автобус",
        cost=100,
        distance=200,
        departure_city=None,
        destination_city=None,
    )
    mock_repo.change_transport.return_value = d_route
    service = DirectoryRouteService(mock_repo)

    result = await service.change_transport(1, "Автобус")

    assert result == d_route
    mock_repo.change_transport.assert_awaited_once_with(1, "Автобус")


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_change_transport(
    mock_repo: Mock,
) -> None:
    mock_repo.change_transport.side_effect = Exception("Error")
    service = DirectoryRouteService(mock_repo)

    with pytest.raises(
        ValueError, match=re.escape("Не получилось изменить транспорт.")
    ):
        await service.change_transport(1, "Поезд")


@pytest.mark.asyncio
async def test_should_successfull_get_by_cities(mock_repo: Mock) -> None:
    d_route = DirectoryRoute(
        d_route_id=1,
        type_transport="Самолет",
        cost=300,
        distance=500,
        departure_city=None,
        destination_city=None,
    )
    mock_repo.get_by_cities.return_value = d_route
    service = DirectoryRouteService(mock_repo)

    result = await service.get_by_cities(1, 2, "Самолет")

    assert result == d_route
    mock_repo.get_by_cities.assert_awaited_once_with(1, 2, "Самолет")


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_get_by_cities(mock_repo: Mock) -> None:
    mock_repo.get_by_cities.side_effect = Exception("Error")
    service = DirectoryRouteService(mock_repo)

    with pytest.raises(
        ValueError, match=re.escape("Справочник маршрутов не получилось удалить.")
    ):
        await service.get_by_cities(1, 2, "Самолет")


@pytest.mark.asyncio
async def test_should_failed_get_list(mock_repo: Mock) -> None:
    mock_repo.get_list.return_value = []
    service = DirectoryRouteService(mock_repo)

    result = await service.get_list()

    assert result == []
    mock_repo.get_list.assert_awaited_once()
