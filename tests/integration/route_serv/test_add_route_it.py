from __future__ import annotations

from datetime import datetime

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from models.accommodation import Accommodation
from models.city import City
from models.directory_route import DirectoryRoute
from models.entertainment import Entertainment
from models.route import Route
from models.travel import Travel
from models.user import User
from services.route_service import RouteService


@pytest.mark.asyncio
async def test_update_route_success(
    route_service: RouteService, db_session: AsyncSession
) -> None:
    d_route = DirectoryRoute(
        d_route_id=1,
        type_transport="Паром",
        cost=3987,
        distance=966,
        departure_city=City(city_id=3, name="Санкт-Петербург"),
        destination_city=City(city_id=5, name="Калининград"),
    )
    user = User(
        user_id=1,
        fio="Лобач Анастасия Олеговна",
        number_passport="1111111111",
        phone_number="89261111111",
        email="nastya@lobach.info",
        login="user1",
        password="123!e5T78",
        is_admin=False,
    )
    accs = [
        Accommodation(
            accommodation_id=1,
            price=46840,
            address="Улица Гоголя, 12",
            name="Four Seasons",
            type="Отель",
            rating=5,
            check_in=datetime(2025, 3, 29, 12, 30, 0),
            check_out=datetime(2025, 4, 5, 18, 0, 0),
            city=City(city_id=1, name="Москва"),
        ),
        Accommodation(
            accommodation_id=2,
            price=7340,
            address="Улица Толстого, 134",
            name="Мир",
            type="Хостел",
            rating=4,
            check_in=datetime(2025, 4, 2, 12, 30, 0),
            check_out=datetime(2025, 4, 5, 18, 0, 0),
            city=City(city_id=1, name="Москва"),
        ),
    ]
    ents = [
        Entertainment(
            entertainment_id=1,
            duration="4 часа",
            address="Главная площадь",
            event_name="Концерт",
            event_time=datetime(2025, 4, 10, 16, 0, 0),
            city=City(city_id=1, name="Москва"),
        ),
        Entertainment(
            entertainment_id=2,
            duration="3 часа",
            address="ул. Кузнецова, 4",
            event_name="Выставка",
            event_time=datetime(2025, 4, 5, 10, 0, 0),
            city=City(city_id=1, name="Москва"),
        ),
    ]
    travels = Travel(
        travel_id=1,
        status="В процессе",
        users=[user],
        accommodations=accs,
        entertainments=ents,
    )
    duplicate_route = Route(
        route_id=4,
        d_route=d_route,
        travels=travels,
        start_time=datetime(2025, 5, 1, 10, 0, 0),
        end_time=datetime(2025, 5, 5, 18, 0, 0),
        type="Свои",
    )
    res = await route_service.add(duplicate_route)
    assert res is not None
