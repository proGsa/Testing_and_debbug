from unittest.mock import AsyncMock, create_autospec, Mock
from typing import cast
import pytest

from repository.city_repository import CityRepository
from repository.directory_route_repository import DirectoryRouteRepository
from repository.accommodation_repository import AccommodationRepository
from repository.entertainment_repository import EntertainmentRepository

@pytest.fixture
def mock_city_repo() -> Mock:
    mock = cast(Mock, create_autospec(CityRepository, instance=True))
    mock.delete = AsyncMock()
    mock.get_list = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.update = AsyncMock()
    mock.add = AsyncMock()
    return mock

@pytest.fixture
def mock_repo() -> Mock:
    repo = Mock(spec=DirectoryRouteRepository, autospec=True)
    repo.get_by_id = AsyncMock()
    repo.get_list = AsyncMock()
    repo.add = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.change_transport = AsyncMock()
    repo.get_by_cities = AsyncMock()
    return repo

@pytest.fixture
def mock_accommodation_repo() -> Mock:
    mock = Mock(spec=AccommodationRepository, autospec=True)
    mock.get_by_id = AsyncMock()
    mock.get_list = AsyncMock()
    mock.add = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    return mock



@pytest.fixture
def mock_entertainment_repo() -> Mock:
    mock = Mock(spec=EntertainmentRepository, autospec=True)
    mock.get_by_id = AsyncMock()
    mock.get_list = AsyncMock()
    mock.add = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    return mock