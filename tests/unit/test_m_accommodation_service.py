from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pytest

from models.accommodation import Accommodation
from services.accommodation_service import AccommodationService


pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_delete_success(mock_accommodation_repo: Mock) -> None:
    service = AccommodationService(mock_accommodation_repo)

    await service.delete(123)

    mock_accommodation_repo.delete.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_delete_failure(mock_accommodation_repo: Mock) -> None:
    mock_accommodation_repo.delete.side_effect = ValueError("Not found")
    service = AccommodationService(mock_accommodation_repo)

    with pytest.raises(ValueError):
        await service.delete(123)


@pytest.mark.asyncio
async def test_should_succesfull_get_existed_accommodation_by_id(
    mock_accommodation_repo: Mock,
) -> None:
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

    mock_accommodation_repo.get_by_id.return_value = accommodation
    service = AccommodationService(mock_accommodation_repo)

    result = await service.get_by_id(1)

    assert result == accommodation
    mock_accommodation_repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_by_id_failure(mock_accommodation_repo: Mock) -> None:
    mock_accommodation_repo.get_by_id.side_effect = ValueError("Not found")
    service = AccommodationService(mock_accommodation_repo)

    with pytest.raises(ValueError):
        await service.get_by_id(123)


@pytest.mark.asyncio
async def test_get_list_success(mock_accommodation_repo: Mock) -> None:
    accommodations = [
        Accommodation(
            accommodation_id=1,
            price=20000,
            address="Улица Гоголя, 12",
            name="Four Seasons",
            type="Отель",
            rating=5,
            check_in=datetime(2023, 10, 10, 10, 0, 0),
            check_out=datetime(2023, 10, 10, 18, 0, 0),
        )
    ]
    mock_accommodation_repo.get_list.return_value = accommodations
    service = AccommodationService(mock_accommodation_repo)

    result = await service.get_list()

    assert result == accommodations
    mock_accommodation_repo.get_list.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_failure(mock_accommodation_repo: Mock) -> None:
    mock_accommodation_repo.get_list.side_effect = ValueError("Database error")
    service = AccommodationService(mock_accommodation_repo)

    with pytest.raises(ValueError):
        await service.get_list()


@pytest.mark.asyncio
async def test_add_success(mock_accommodation_repo: Mock) -> None:
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
    mock_accommodation_repo.add.return_value = accommodation
    service = AccommodationService(mock_accommodation_repo)

    result = await service.add(accommodation)

    assert result == accommodation
    mock_accommodation_repo.add.assert_awaited_once_with(accommodation)


@pytest.mark.asyncio
async def test_add_failure(mock_accommodation_repo: Mock) -> None:
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
    mock_accommodation_repo.add.side_effect = ValueError("Duplicate")
    service = AccommodationService(mock_accommodation_repo)

    with pytest.raises(ValueError):
        await service.add(accommodation)


@pytest.mark.asyncio
async def test_update_success(mock_accommodation_repo: Mock) -> None:
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
    service = AccommodationService(mock_accommodation_repo)
    mock_accommodation_repo.update.return_value = accommodation

    result = await service.update(accommodation)

    assert result == accommodation
    mock_accommodation_repo.update.assert_awaited_once_with(accommodation)


@pytest.mark.asyncio
async def test_update_failure(mock_accommodation_repo: Mock) -> None:
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
    mock_accommodation_repo.update.side_effect = ValueError("Not found")
    service = AccommodationService(mock_accommodation_repo)

    with pytest.raises(ValueError):
        await service.update(accommodation)
