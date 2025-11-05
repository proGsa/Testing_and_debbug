from __future__ import annotations

import asyncio
import uuid

from datetime import datetime
from typing import AsyncGenerator
from typing import cast
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import create_autospec

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

from repository.accommodation_repository import AccommodationRepository
from repository.city_repository import CityRepository
from repository.directory_route_repository import DirectoryRouteRepository
from repository.entertainment_repository import EntertainmentRepository
from repository.route_repository import RouteRepository
from repository.travel_repository import TravelRepository
from repository.user_repository import UserRepository
from services.accommodation_service import AccommodationService
from services.city_service import CityService
from services.directory_route_service import DirectoryRouteService
from services.entertainment_service import EntertainmentService
from services.route_service import RouteService
from services.travel_service import TravelService
from services.user_service import AuthService
from services.user_service import UserService
import warnings
from sqlalchemy.exc import SAWarning
import logging

# Игнорируем все SAWarning
warnings.filterwarnings("ignore", category=SAWarning)
warnings.filterwarnings("ignore", message="Event loop is closed")
warnings.filterwarnings("ignore", message="The garbage collector is trying to clean up non-checked-in connection")

logging.getLogger("sqlalchemy.pool").setLevel(logging.CRITICAL)

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


@pytest_asyncio.fixture(scope="session")
async def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# engine = create_async_engine("postgresql+asyncpg://nastya:nastya@localhost:5434/mydb", echo=True)
engine = create_async_engine("postgresql+asyncpg://test_user:test_password@localhost:5432/test_db", echo=True)

AsyncSessionMaker: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    schema_name = f"test_{uuid.uuid4().hex[:8]}"
    
    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA {schema_name}"))
    
    try:
        async with AsyncSessionMaker() as session:
            await session.execute(text(f"SET search_path TO {schema_name}"))
            
            await create_tables(session)
            
            await fill_test_data(session)
            await session.commit()
            
            try:
                yield session
            finally:
                await session.rollback()
                await session.close()
    
    finally:
        async with engine.begin() as conn:
            await conn.execute(text(f"DROP SCHEMA {schema_name} CASCADE"))


async def create_tables(session: AsyncSession) -> None:
    tables = [
        """
        CREATE TABLE city (
            city_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE entertainment (
            id SERIAL PRIMARY KEY,
            duration VARCHAR NOT NULL,
            address VARCHAR NOT NULL,
            event_name VARCHAR NOT NULL UNIQUE,
            event_time TIMESTAMP NOT NULL,
            city INTEGER REFERENCES city(city_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE accommodations (
            id SERIAL PRIMARY KEY,
            price INTEGER NOT NULL,
            address VARCHAR NOT NULL,
            name VARCHAR NOT NULL UNIQUE,
            type VARCHAR NOT NULL,
            rating INTEGER NOT NULL,
            check_in TIMESTAMP NOT NULL,
            check_out TIMESTAMP NOT NULL, 
            city INTEGER NOT NULL REFERENCES city(city_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE directory_route (
            id SERIAL PRIMARY KEY,
            type_transport VARCHAR NOT NULL,
            departure_city INT REFERENCES city(city_id) ON DELETE CASCADE,
            arrival_city INT REFERENCES city(city_id) ON DELETE CASCADE,
            distance INT NOT NULL,
            price INT NOT NULL
        )
        """,
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR NOT NULL,
            passport VARCHAR NOT NULL UNIQUE,
            phone VARCHAR NOT NULL UNIQUE,
            email VARCHAR NOT NULL UNIQUE,
            login VARCHAR NOT NULL UNIQUE,
            password VARCHAR NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT FALSE
        )
        """,
        """
        CREATE TABLE travel (
            id SERIAL PRIMARY KEY,
            status VARCHAR NOT NULL,
            user_id INT NOT NULL
        )
        """,
        """
        CREATE TABLE travel_entertainment (
            id SERIAL PRIMARY KEY,
            travel_id INT NOT NULL,
            entertainment_id INT NOT NULL,
            CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel(id) ON DELETE CASCADE,
            CONSTRAINT fk_entertainment_id FOREIGN KEY (entertainment_id) REFERENCES entertainment(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE travel_accommodations (
            id SERIAL PRIMARY KEY,
            travel_id INT NOT NULL,
            accommodation_id INT NOT NULL,
            CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel(id) ON DELETE CASCADE,
            CONSTRAINT fk_accommodation_id FOREIGN KEY (accommodation_id) REFERENCES accommodations(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE users_travel (
            id SERIAL PRIMARY KEY,
            travel_id INT NOT NULL,
            users_id INT NOT NULL,
            CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel(id) ON DELETE CASCADE,
            CONSTRAINT fk_users_id FOREIGN KEY (users_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE route (
            id SERIAL PRIMARY KEY,
            d_route_id INT NOT NULL,
            travel_id INT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            type VARCHAR(20) NOT NULL,
            CONSTRAINT fk_d_route_id FOREIGN KEY (d_route_id) REFERENCES directory_route(id) ON DELETE CASCADE,
            CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel(id) ON DELETE CASCADE
        )
        """
    ]
    
    for table_sql in tables:
        await session.execute(text(table_sql))


async def fill_test_data(session: AsyncSession) -> None:
    await session.execute(text("""
        INSERT INTO city (name) VALUES 
        ('Москва'), ('Воронеж'), ('Санкт-Петербург'), 
        ('Екатеринбург'), ('Калининград')
        """))
    entertainment_data = [
        {"duration": "4 часа", "address": "Главная площадь", "event_name": "Концерт", 
                                            "event_time": datetime(2025, 4, 10, 16, 0, 0), "city": 1},
        {"duration": "3 часа", "address": "ул. Кузнецова, 4", "event_name": "Выставка", 
                                            "event_time": datetime(2025, 4, 5, 10, 0, 0), "city": 1}
    ]
    for data in entertainment_data:
        await session.execute(text("""
            INSERT INTO entertainment 
            (duration, address, event_name, event_time, city) 
            VALUES (:duration, :address, :event_name, :event_time, :city)"""), data)
    await session.commit()
    accommodations_data = [
        {"price": 33450, "address": "ул. Дмитриевского, 7", "name": "ABC",
            "type": "Квартира", "rating": 3, "check_in": datetime(2025, 4, 2, 14, 0, 0), "check_out": datetime(2025, 4, 6, 18, 0, 0), "city": 1},
        {
            "price": 46840, "address": "Улица Гоголя, 12", "name": "Four Seasons",
            "type": "Отель", "rating": 5, "check_in": datetime(2025, 3, 29, 12, 30, 0), "check_out": datetime(2025, 4, 5, 18, 0, 0), "city": 1  
        }
    ]

    for data in accommodations_data:
        await session.execute(text("""
            INSERT INTO accommodations 
            (price, address, name, type, rating, check_in, check_out, city) 
            VALUES (:price, :address, :name, :type, :rating, :check_in, :check_out, :city)
        """), data)

    d_routes = [
        {"type_transport": "Паром", "departure_city": 3, "arrival_city": 5, "distance": 966, "price": 3987},
        {"type_transport": "Самолет", "departure_city": 3, "arrival_city": 5, "distance": 966, "price": 5123},
        {"type_transport": "Автобус", "departure_city": 3, "arrival_city": 4, "distance": 1840, "price": 3796},
        {"type_transport": "Поезд", "departure_city": 3, "arrival_city": 5, "distance": 966, "price": 2541},
        {"type_transport": "Автобус", "departure_city": 3, "arrival_city": 5, "distance": 966, "price": 4756},
        {"type_transport": "Самолет", "departure_city": 3, "arrival_city": 4, "distance": 1840, "price": 8322},
        {"type_transport": "Поезд", "departure_city": 3, "arrival_city": 4, "distance": 1840, "price": 4305},
        {"type_transport": "Самолет", "departure_city": 5, "arrival_city": 4, "distance": 3025, "price": 10650},
        {"type_transport": "Поезд", "departure_city": 5, "arrival_city": 4, "distance": 3025, "price": 5988},
        {"type_transport": "Самолет", "departure_city": 1, "arrival_city": 2, "distance": 467, "price": 2223},
        {"type_transport": "Поезд", "departure_city": 1, "arrival_city": 2, "distance": 515, "price": 1911},
        {"type_transport": "Поезд", "departure_city": 4, "arrival_city": 1, "distance": 1780, "price": 3500},
    ]
    for data in d_routes:
        await session.execute(text("INSERT INTO directory_route (type_transport, departure_city, \
                arrival_city, distance, price) \
            VALUES (:type_transport, :departure_city, :arrival_city, :distance, :price)"), data)
    users = [
        {"fio": "Лобач Анастасия Олеговна", "number_passport": "1111111111", "phone_number": "89261111111", "email": "nastya@lobach.info", "login": "user1", "password": "123!e5T78"},
        {"fio": "Иванов Иван Иванович", "number_passport": "2222222222", "phone_number": "89262222222", "email": "ivanov@ivanov.com", "login": "user2", "password": "456!f6R89"},
        {"fio": "Петров Петр Петрович", "number_passport": "3333333333", "phone_number": "89263333333", "email": "petrov@petrov.com", "login": "user3", "password": "789!g7T90"}
    ]
    for user_data in users:
        await session.execute(text("""
            INSERT INTO users (full_name, passport, phone, email, login, password, is_admin)
            VALUES (:fio, :number_passport, :phone_number, :email, :login, :password, false)
        """), user_data)

    travels_data = [{"status": "В процессе", "user_id": 1}, {"status": "Завершен", "user_id": 1}]
    tr_ent = [(1, 2), (2, 1)]
    tr_a = [(1, 1), (2, 2)]

    for i, travel_data in enumerate(travels_data, 1):
        await session.execute(text("""
            INSERT INTO travel (id, status, user_id) VALUES (:id, :status, :user_id)
        """), {"id": i, "status": travel_data["status"], "user_id": travel_data["user_id"]})
    for t in tr_ent:
        await session.execute(
            text("INSERT INTO travel_entertainment (travel_id, entertainment_id) \
                VALUES (:travel_id, :entertainment_id)"), 
                {"travel_id": t[0], "entertainment_id": t[1]}
        )
    for t in tr_a:
        await session.execute(
            text("INSERT INTO travel_accommodations (travel_id, accommodation_id) \
                VALUES (:travel_id, :accommodation_id)"),
                    {"travel_id": t[0], "accommodation_id": t[1]}
        )
    route = [
        {"d_route_id": 1, "travel_id": 1, "start_time": datetime(2025, 4, 2, 7, 30, 0),
                                "end_time": datetime(2025, 4, 6, 7, 0, 0), "type": "Свои"}, 
        {"d_route_id": 9, "travel_id": 1, "start_time": datetime(2025, 4, 3, 7, 30, 0),
                                "end_time": datetime(2025, 4, 6, 7, 0, 0), "type": "Свои"},
        {"d_route_id": 11, "travel_id": 2, "start_time": datetime(2025, 3, 29, 6, 50, 0), 
                                "end_time": datetime(2025, 4, 5, 22, 45, 0), "type": "Свои"}]
    for data in route:
        await session.execute(
            text("INSERT INTO route (d_route_id, travel_id, start_time, end_time, type) \
                VALUES (:d_route_id, :travel_id, :start_time, :end_time, :type)"),
                    {
                        "d_route_id": data["d_route_id"],
                        "travel_id": data["travel_id"],
                        "start_time": data["start_time"],
                        "end_time": data["end_time"],
                        "type": data["type"],
                    }
                )
    await session.execute(
        text("INSERT INTO users_travel (travel_id, users_id) VALUES (:travel_id, :users_id)"),
        {"travel_id": 1, "users_id": 1})
    await session.execute(
        text("INSERT INTO users_travel (travel_id, users_id) VALUES (:travel_id, :users_id)"),
        {"travel_id": 2, "users_id": 1})
    await session.commit()


@pytest_asyncio.fixture
async def city_repo(db_session: AsyncSession) -> CityRepository:
    return CityRepository(db_session)


@pytest_asyncio.fixture
async def city_service(city_repo: CityRepository) -> CityService:
    return CityService(city_repo)


@pytest_asyncio.fixture
async def accommodation_repo(db_session: AsyncSession, city_repo: CityRepository) -> AccommodationRepository:
    return AccommodationRepository(db_session, city_repo)


@pytest_asyncio.fixture
async def accommodation_service(accommodation_repo: AccommodationRepository) -> AccommodationService:
    return AccommodationService(accommodation_repo)


@pytest_asyncio.fixture
async def entertainment_repo(db_session: AsyncSession, city_repo: CityRepository) -> EntertainmentRepository:
    return EntertainmentRepository(db_session, city_repo)


@pytest_asyncio.fixture
async def entertainment_service(entertainment_repo: EntertainmentRepository) -> EntertainmentService:
    return EntertainmentService(entertainment_repo)


@pytest_asyncio.fixture
async def directory_route_repo(db_session: AsyncSession, city_repo: CityRepository) -> DirectoryRouteRepository:
    return DirectoryRouteRepository(db_session, city_repo)


@pytest_asyncio.fixture
async def d_route_service(directory_route_repo: DirectoryRouteRepository) -> DirectoryRouteService:
    return DirectoryRouteService(directory_route_repo)


@pytest_asyncio.fixture
async def user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(db_session)


@pytest_asyncio.fixture
async def user_service(user_repo: UserRepository) -> UserService:
    return UserService(user_repo)


@pytest_asyncio.fixture
async def auth_service(user_repo: UserRepository) -> AuthService:
    return AuthService(user_repo)


@pytest_asyncio.fixture
async def route_repo(db_session: AsyncSession, directory_route_repo: DirectoryRouteRepository, travel_repo: TravelRepository) -> RouteRepository:
    return RouteRepository(db_session, directory_route_repo, travel_repo)


@pytest_asyncio.fixture
async def route_service(route_repo: RouteRepository) -> RouteService:
    return RouteService(route_repo)


@pytest_asyncio.fixture
async def travel_repo(db_session: AsyncSession, user_repo: UserRepository, accommodation_repo: AccommodationRepository, entertainment_repo: EntertainmentRepository) -> TravelRepository:
    return TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)


@pytest_asyncio.fixture
async def travel_service(db_session: AsyncSession) -> TravelService:
    user_repo = UserRepository(db_session)
    city_repo = CityRepository(db_session)
    entertainment_repo = EntertainmentRepository(db_session, city_repo)
    accommodation_repo = AccommodationRepository(db_session, city_repo)
    travel_repo = TravelRepository(db_session, user_repo, entertainment_repo, accommodation_repo)
    return TravelService(travel_repo)
