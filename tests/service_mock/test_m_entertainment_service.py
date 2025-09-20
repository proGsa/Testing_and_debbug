from __future__ import annotations

import re

from datetime import datetime
from unittest.mock import Mock

import pytest

from models.entertainment import Entertainment
from services.entertainment_service import EntertainmentService


pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_service_should_successfull_delete_existed_entertainment(mock_entertainment_repo: Mock) -> None:
    service = EntertainmentService(mock_entertainment_repo)

    await service.delete(123)

    mock_entertainment_repo.delete.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_service_should_throw_exception_at_delete_not_existed_entertainment(mock_entertainment_repo: Mock) -> None:
    mock_entertainment_repo.delete.side_effect = Exception("Not found")
    service = EntertainmentService(mock_entertainment_repo)

    with pytest.raises(ValueError, match=re.escape("Развлечение не найдено.")):
        await service.delete(123)
    
    mock_entertainment_repo.delete.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_should_succesfull_get_existed_entertainment_by_id(mock_entertainment_repo: Mock) -> None:
    entertainment = Entertainment(
        entertainment_id=1,
        duration="4 часа",
        address="Главная площадь",
        event_name="Концерт",
        event_time=datetime(2023, 10, 10, 10, 0, 0)
    )
    mock_entertainment_repo.get_by_id.return_value = entertainment
    service = EntertainmentService(mock_entertainment_repo)

    result = await service.get_by_id(1)

    assert result == entertainment
    mock_entertainment_repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_by_id_failure(mock_entertainment_repo: Mock) -> None:
    mock_entertainment_repo.get_by_id.side_effect = ValueError("Not found")
    service = EntertainmentService(mock_entertainment_repo)

    with pytest.raises(ValueError):
        await service.get_by_id(123)


@pytest.mark.asyncio
async def test_get_list_success(mock_entertainment_repo: Mock) -> None:
    entertainments = [
        Entertainment(
            entertainment_id=1,
            duration="4 часа",
            address="Главная площадь",
            event_name="Концерт",
            event_time=datetime(2023, 10, 10, 10, 0, 0)
        )
    ]
    mock_entertainment_repo.get_list.return_value = entertainments
    service = EntertainmentService(mock_entertainment_repo)

    result = await service.get_list()

    assert result == entertainments
    mock_entertainment_repo.get_list.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_failure(mock_entertainment_repo: Mock) -> None:
    mock_entertainment_repo.get_list.side_effect = ValueError("Database error")
    service = EntertainmentService(mock_entertainment_repo)

    with pytest.raises(ValueError):
        await service.get_list()


@pytest.mark.asyncio
async def test_add_success(mock_entertainment_repo: Mock) -> None:
    entertainment = Entertainment(
        entertainment_id=1,
        duration="4 часа",
        address="Главная площадь",
        event_name="Концерт",
        event_time=datetime(2023, 10, 10, 10, 0, 0)
    )
    mock_entertainment_repo.add.return_value = entertainment
    service = EntertainmentService(mock_entertainment_repo)

    result = await service.add(entertainment)

    assert result == entertainment
    mock_entertainment_repo.add.assert_awaited_once_with(entertainment)


@pytest.mark.asyncio
async def test_add_failure(mock_entertainment_repo: Mock) -> None:
    entertainment = Entertainment(
        entertainment_id=1,
        duration="4 часа",
        address="Главная площадь",
        event_name="Концерт",
        event_time=datetime(2023, 10, 10, 10, 0, 0)
    )
    mock_entertainment_repo.add.side_effect = ValueError("Duplicate")
    service = EntertainmentService(mock_entertainment_repo)

    with pytest.raises(ValueError):
        await service.add(entertainment)


@pytest.mark.asyncio
async def test_update_success(mock_entertainment_repo: Mock) -> None:
    entertainment = Entertainment(
        entertainment_id=1,
        duration="4 часа",
        address="Главная площадь",
        event_name="Концерт",
        event_time=datetime(2023, 10, 10, 10, 0, 0)
    )
    mock_entertainment_repo.update.return_value = entertainment
    service = EntertainmentService(mock_entertainment_repo)

    result = await service.update(entertainment)

    assert result == entertainment
    mock_entertainment_repo.update.assert_awaited_once_with(entertainment)


@pytest.mark.asyncio
async def test_update_failure(mock_entertainment_repo: Mock) -> None:
    entertainment = Entertainment(
        entertainment_id=1,
        duration="4 часа",
        address="Главная площадь",
        event_name="Концерт",
        event_time=datetime(2023, 10, 10, 10, 0, 0)
    )
    mock_entertainment_repo.update.side_effect = ValueError("Not found")
    service = EntertainmentService(mock_entertainment_repo)

    with pytest.raises(ValueError):
        await service.update(entertainment)
