from __future__ import annotations

import re

from datetime import datetime
from typing import cast
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from abstract_repository.itravel_repository import ITravelRepository
from models.accommodation import Accommodation
from models.entertainment import Entertainment
from models.travel import Travel
from models.user import User
from services.travel_service import TravelService


TWO = 2
pytestmark = pytest.mark.unit


def create_test_travel(travel_id: int = 1) -> Travel:
    accommodation = Accommodation(
        accommodation_id=1,
        price=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        type="Отель",
        rating=5,
        check_in=datetime(2023, 10, 10, 10, 0, 0),
        check_out=datetime(2023, 10, 10, 18, 0, 0),
    )

    entertainment = Entertainment(
        entertainment_id=1,
        duration="4 часа",
        address="главная площадь",
        event_name="Концерт",
        event_time=datetime(2023, 10, 10, 10, 0, 0),
    )

    return Travel(
        travel_id=travel_id,
        status="В процессе",
        users=[create_test_user()],
        accommodations=[accommodation],
        entertainments=[entertainment],
    )


def create_test_user(user_id: int = 1) -> User:
    return User(
        user_id=user_id,
        fio="Test User",
        number_passport="1234567890",
        phone_number="89256482340",
        email="test@example.com",
        login="adkakfsne",
        password="password123!Q",
    )


def create_mock_repository() -> ITravelRepository:
    mock_repo = AsyncMock(spec=ITravelRepository, autospec=True)

    mock_repo.get_by_id = AsyncMock()
    mock_repo.get_list = AsyncMock()
    mock_repo.add = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    mock_repo.search = AsyncMock()
    mock_repo.complete = AsyncMock()
    mock_repo.get_users_by_travel = AsyncMock()
    mock_repo.get_entertainments_by_travel = AsyncMock()
    mock_repo.get_accommodations_by_travel = AsyncMock()
    mock_repo.link_entertainments = AsyncMock()
    mock_repo.link_users = AsyncMock()
    mock_repo.link_accommodations = AsyncMock()
    mock_repo.get_travels_for_user = AsyncMock()
    mock_repo.get_travel_by_route_id = AsyncMock()

    return cast(ITravelRepository, mock_repo)


@pytest.mark.asyncio
async def test_get_by_id_not_found() -> None:
    with patch.object(TravelService, "__init__", return_value=None):
        mock_repo = create_mock_repository()
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_by_id.return_value = None

        result = await service.get_by_id(999)

        service.repository.get_by_id.assert_called_once_with(999)
        assert result is None


@pytest.mark.asyncio
async def test_get_all_travels_success() -> None:
    test_travels = [create_test_travel(1), create_test_travel(2)]

    with patch.object(TravelService, "__init__", return_value=None):
        mock_repo = create_mock_repository()
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_list.return_value = test_travels

        result = await service.get_all_travels()

        service.repository.get_list.assert_called_once()
        assert result == test_travels
        assert len(result) == TWO


@pytest.mark.asyncio
async def test_get_all_travels_empty() -> None:
    with patch.object(TravelService, "__init__", return_value=None):
        mock_repo = create_mock_repository()
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_list.return_value = []

        result = await service.get_all_travels()

        service.repository.get_list.assert_called_once()
        assert result == []
        assert len(result) == 0


@pytest.mark.asyncio
async def test_add_travel_success() -> None:
    test_travel = create_test_travel()

    with patch.object(TravelService, "__init__", return_value=None):
        mock_repo = create_mock_repository()
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.add.return_value = test_travel

        result = await service.add(test_travel)

        service.repository.add.assert_called_once_with(test_travel)
        assert result == test_travel


@pytest.mark.asyncio
async def test_add_travel_duplicate_id() -> None:
    mock_repo = create_mock_repository()
    test_travel = create_test_travel()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.add.side_effect = Exception("Duplicate ID")

        with pytest.raises(
            ValueError, match=re.escape("Путешествие c таким ID уже существует.")
        ):
            await service.add(test_travel)

        service.repository.add.assert_called_once_with(test_travel)


@pytest.mark.asyncio
async def test_update_travel_success() -> None:
    test_travel = create_test_travel()
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.update.return_value = None

        result = await service.update(test_travel)

        service.repository.update.assert_called_once_with(test_travel)
        assert result == test_travel


@pytest.mark.asyncio
async def test_update_travel_not_found() -> None:
    test_travel = create_test_travel(999)
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.update.side_effect = Exception("Not found")

        with pytest.raises(ValueError, match=re.escape("Путешествие не найдено.")):
            await service.update(test_travel)

        service.repository.update.assert_called_once_with(test_travel)


@pytest.mark.asyncio
async def test_delete_travel_success() -> None:
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.delete.return_value = None

        await service.delete(1)

        service.repository.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_travel_not_found() -> None:
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.delete.side_effect = Exception("Not found")

        with pytest.raises(ValueError, match=re.escape("Путешествие не найдено.")):
            await service.delete(999)

        service.repository.delete.assert_called_once_with(999)


@pytest.mark.asyncio
async def test_search_travels_success() -> None:
    test_travels = [create_test_travel(1), create_test_travel(2)]
    search_params = {"status": "В процессе"}
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.search.return_value = test_travels

        result = await service.search(search_params)

        service.repository.search.assert_called_once_with(search_params)
        assert result == test_travels
        assert len(result) == TWO


@pytest.mark.asyncio
async def test_search_travels_not_found() -> None:
    search_params = {"status": "Несуществующий статус"}
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.search.side_effect = Exception("Not found")

        with pytest.raises(
            ValueError,
            match=re.escape("Путешествие по переданным параметрам не найдено."),
        ):
            await service.search(search_params)

        service.repository.search.assert_called_once_with(search_params)


@pytest.mark.asyncio
async def test_complete_travel_success() -> None:
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.complete.return_value = None

        await service.complete(1)

        service.repository.complete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_complete_travel_error() -> None:
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.complete.side_effect = Exception("Error")

        with pytest.raises(
            ValueError, match=re.escape("Ошибка при завершении путешествия")
        ):
            await service.complete(1)

        service.repository.complete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_users_by_travel_success() -> None:
    test_users = [create_test_user(1), create_test_user(2)]
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_users_by_travel.return_value = test_users

        result = await service.get_users_by_travel(1)

        service.repository.get_users_by_travel.assert_called_once_with(1)
        assert result == test_users
        assert len(result) == TWO


@pytest.mark.asyncio
async def test_get_users_by_travel_error() -> None:
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_users_by_travel.side_effect = Exception("Error")

        with pytest.raises(
            ValueError, match=re.escape("Ошибка при получении пользователей")
        ):
            await service.get_users_by_travel(1)

        service.repository.get_users_by_travel.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_entertainments_by_travel_success() -> None:
    entertainment = Entertainment(
        entertainment_id=1,
        duration="4 часа",
        address="главная площадь",
        event_name="Концерт",
        event_time=datetime(2023, 10, 10, 10, 0, 0),
    )
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_entertainments_by_travel.return_value = [entertainment]

        result = await service.get_entertainments_by_travel(1)

        service.repository.get_entertainments_by_travel.assert_called_once_with(1)
        assert len(result) == 1
        assert result[0].entertainment_id == 1


@pytest.mark.asyncio
async def test_get_entertainments_by_travel_error() -> None:
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_entertainments_by_travel.side_effect = Exception("Error")

        with pytest.raises(
            ValueError,
            match=re.escape("Ошибка при получении развлечений для путешествий"),
        ):
            await service.get_entertainments_by_travel(1)

        service.repository.get_entertainments_by_travel.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_accommodations_by_travel_success() -> None:
    accommodation = Accommodation(
        accommodation_id=1,
        price=20000,
        address="Улица Гоголя, 12",
        name="Four Seasons",
        type="Отель",
        rating=5,
        check_in=datetime(2023, 10, 10, 10, 0, 0),
        check_out=datetime(2023, 10, 10, 18, 0, 0),
    )
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_accommodations_by_travel.return_value = [accommodation]

        result = await service.get_accommodations_by_travel(1)

        service.repository.get_accommodations_by_travel.assert_called_once_with(1)
        assert len(result) == 1
        assert result[0].accommodation_id == 1


@pytest.mark.asyncio
async def test_get_accommodations_by_travel_error() -> None:
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_accommodations_by_travel.side_effect = Exception("Error")

        with pytest.raises(
            ValueError, match=re.escape("Ошибка при получении завершенных путешествий")
        ):
            await service.get_accommodations_by_travel(1)

        service.repository.get_accommodations_by_travel.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_link_entertainments_success() -> None:
    entertainment_ids = [1, 2, 3]
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.link_entertainments.return_value = None

        await service.link_entertainments(1, entertainment_ids)

        service.repository.link_entertainments.assert_called_once_with(
            1, entertainment_ids
        )


@pytest.mark.asyncio
async def test_link_entertainments_error() -> None:
    entertainment_ids = [1, 2, 3]
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.link_entertainments.side_effect = Exception("Error")

        with pytest.raises(
            ValueError,
            match=re.escape("Ошибка при связывании развлечений с путешествием."),
        ):
            await service.link_entertainments(1, entertainment_ids)

        service.repository.link_entertainments.assert_called_once_with(
            1, entertainment_ids
        )


@pytest.mark.asyncio
async def test_link_users_success() -> None:
    user_ids = [1, 2, 3]
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.link_users.return_value = None

        await service.link_users(1, user_ids)

        service.repository.link_users.assert_called_once_with(1, user_ids)


@pytest.mark.asyncio
async def test_link_users_error() -> None:
    user_ids = [1, 2, 3]
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.link_users.side_effect = Exception("Error")

        with pytest.raises(
            ValueError,
            match=re.escape("Ошибка при связывании пользователей с путешествием."),
        ):
            await service.link_users(1, user_ids)

        service.repository.link_users.assert_called_once_with(1, user_ids)


@pytest.mark.asyncio
async def test_link_accommodations_success() -> None:
    accommodation_ids = [1, 2, 3]
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.link_accommodations.return_value = None

        await service.link_accommodations(1, accommodation_ids)

        service.repository.link_accommodations.assert_called_once_with(
            1, accommodation_ids
        )


@pytest.mark.asyncio
async def test_link_accommodations_error() -> None:
    accommodation_ids = [1, 2, 3]
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.link_accommodations.side_effect = Exception("Error")

        with pytest.raises(
            ValueError,
            match=re.escape("Ошибка при связывании мест проживания с путешествием."),
        ):
            await service.link_accommodations(1, accommodation_ids)

        service.repository.link_accommodations.assert_called_once_with(
            1, accommodation_ids
        )


@pytest.mark.asyncio
async def test_get_travels_for_user_success() -> None:
    test_travels = [create_test_travel(1), create_test_travel(2)]
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_travels_for_user.return_value = test_travels

        result = await service.get_travels_for_user(1, "active")

        service.repository.get_travels_for_user.assert_called_once_with(1, "active")
        assert result == test_travels
        assert len(result) == TWO


@pytest.mark.asyncio
async def test_get_travels_for_user_error() -> None:
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_travels_for_user.side_effect = Exception("Error")

        with pytest.raises(
            ValueError, match=re.escape("Ошибка при получении активных путешествий")
        ):
            await service.get_travels_for_user(1, "active")

        service.repository.get_travels_for_user.assert_called_once_with(1, "active")


@pytest.mark.asyncio
async def test_get_travel_by_route_id_success() -> None:
    test_travel = create_test_travel()
    mock_repo = create_mock_repository()
    with patch.object(TravelService, "__init__", return_value=None):
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_travel_by_route_id.return_value = test_travel

        result = await service.get_travel_by_route_id(123)

        service.repository.get_travel_by_route_id.assert_called_once_with(123)
        assert result == test_travel


@pytest.mark.asyncio
async def test_get_travel_by_route_id_not_found() -> None:
    with patch.object(TravelService, "__init__", return_value=None):
        mock_repo = create_mock_repository()
        service = TravelService(mock_repo)
        service.repository = AsyncMock()
        service.repository.get_travel_by_route_id.side_effect = Exception("Not found")

        with pytest.raises(ValueError):
            await service.get_travel_by_route_id(999)

        service.repository.get_travel_by_route_id.assert_called_once_with(999)
