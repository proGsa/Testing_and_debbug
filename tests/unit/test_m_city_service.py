from __future__ import annotations

import re

from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from models.city import City
from repository.city_repository import CityRepository
from services.city_service import CityService


pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_service_should_successfull_delete_existed_city(mock_city_repo: Mock) -> None:
    # Arrange
    city_service = CityService(mock_city_repo)
    
    # Act
    await city_service.delete(123)
    
    # Assert
    mock_city_repo.delete.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_delete_not_existed_city() -> None:
    repository = Mock(spec=CityRepository)
    repository.delete = AsyncMock(side_effect=ValueError("Not found"))

    city_service = CityService(repository)

    with pytest.raises(ValueError):
        await city_service.delete(123)


@pytest.mark.asyncio
async def test_should_succesfull_get_cities() -> None:
    cities = [
        City(city_id=1, name="Москва"),
        City(city_id=2, name="Казань")
    ]
    repository = Mock(spec=CityRepository)
    repository.get_list = AsyncMock(return_value=cities)

    city_service = CityService(repository)
    result = await city_service.get_all_cities()

    assert result == cities
    repository.get_list.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_should_call_get_list_on_repository() -> None:
    repository = Mock(spec=CityRepository)
    repository.get_list = AsyncMock()

    city_service = CityService(repository)

    await city_service.get_all_cities()

    repository.get_list.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_success() -> None:
    city = City(city_id=3, name="Воронеж")
    repo = Mock(spec=CityRepository)
    repo.add = AsyncMock(return_value=city)

    service = CityService(repo)
    result = await service.add(city)

    assert result == city
    repo.add.assert_awaited_once_with(city)


@pytest.mark.asyncio
async def test_add_failure_duplicate() -> None:
    city = City(city_id=3, name="Воронеж")
    repo = Mock(spec=CityRepository)
    repo.add = AsyncMock(side_effect=Exception("Duplicate"))

    service = CityService(repo)

    with pytest.raises(ValueError, match=re.escape("Город c таким ID уже существует.")):
        await service.add(city)


@pytest.mark.asyncio
async def test_get_all_cities_failure() -> None:
    repo = Mock(spec=CityRepository)
    repo.get_list = AsyncMock(side_effect=Exception("db error"))

    service = CityService(repo)

    with pytest.raises(Exception, match="db error"):
        await service.get_all_cities()


@pytest.mark.asyncio
async def test_should_succesfull_get_existed_city_by_id() -> None:
    city = City(city_id=1, name="Москва")
    repository = Mock(spec=CityRepository)
    repository.get_by_id = AsyncMock(return_value=city)

    city_service = CityService(repository)
    result = await city_service.get_by_id(1)

    assert result == city
    repository.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_service_should_call_get_by_id_on_repository() -> None:
    repository = Mock(spec=CityRepository)
    repository.get_by_id = AsyncMock()

    city_service = CityService(repository)

    await city_service.get_by_id(1)

    repository.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_get_not_existed_city() -> None:
    repository = Mock(spec=CityRepository)
    repository.get_by_id = AsyncMock(side_effect=ValueError("Not found"))

    city_service = CityService(repository)

    with pytest.raises(ValueError):
        await city_service.get_by_id(123)


@pytest.mark.asyncio
async def test_should_succesfull_update_existed_city_by_id() -> None:
    city = City(city_id=1, name="Москва")
    repository = Mock(spec=CityRepository)
    repository.update = AsyncMock(return_value=city)

    city_service = CityService(repository)
    result = await city_service.update(city)

    assert result == city
    repository.update.assert_awaited_once_with(city)


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_update_not_existed_city() -> None:
    city = City(city_id=1, name="Москва")
    repository = Mock(spec=CityRepository)
    repository.update = AsyncMock(side_effect=ValueError("Not found"))

    city_service = CityService(repository)

    with pytest.raises(ValueError):
        await city_service.update(city)