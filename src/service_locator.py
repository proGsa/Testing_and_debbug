from __future__ import annotations

import asyncio
import logging

from dataclasses import dataclass
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from abstract_repository.iaccommodation_repository import IAccommodationRepository
from abstract_repository.icity_repository import ICityRepository
from abstract_repository.idirectory_route_repository import IDirectoryRouteRepository
from abstract_repository.ientertainment_repository import IEntertainmentRepository
from abstract_repository.iroute_repository import IRouteRepository
from abstract_repository.itravel_repository import ITravelRepository
from abstract_repository.iuser_repository import IUserRepository
from controllers.accommodation_controller import AccommodationController
from controllers.city_controller import CityController
from controllers.d_route_controller import DirectoryRouteController
from controllers.entertainment_controller import EntertainmentController
from controllers.route_controller import RouteController
from controllers.travel_controller import TravelController
from controllers.user_controller import UserController
from repository.accommodation_repository import AccommodationRepository
from repository.city_repository import CityRepository
from repository.directory_route_repository import DirectoryRouteRepository
from repository.entertainment_repository import EntertainmentRepository
from repository.route_repository import RouteRepository
from repository.travel_repository import TravelRepository
from repository.user_repository import UserRepository
from repository_mongodb.accommodation_repository import AccommodationRepository as MongoAccommodationRepository
from repository_mongodb.city_repository import CityRepository as MongoCityRepository
from repository_mongodb.directory_route_repository import DirectoryRouteRepository as MongoDirectoryRouteRepository
from repository_mongodb.entertainment_repository import EntertainmentRepository as MongoEntertainmentRepository
from repository_mongodb.route_repository import RouteRepository as MongoRouteRepository
from repository_mongodb.travel_repository import TravelRepository as MongoTravelRepository
from repository_mongodb.user_repository import UserRepository as MongoUserRepository
from services.accommodation_service import AccommodationService
from services.city_service import CityService
from services.directory_route_service import DirectoryRouteService
from services.entertainment_service import EntertainmentService
from services.route_service import RouteService
from services.travel_service import TravelService
from services.user_service import AuthService
from services.user_service import UserService
from settings import settings


logger = logging.getLogger(__name__)

_mongo_client: AsyncIOMotorClient[Any] | None = None
_async_session_maker = None


@dataclass
class Repositories:
    def __init__(
            self,
            acc_repo: IAccommodationRepository,
            city_repo: ICityRepository,
            d_route_repo: IDirectoryRouteRepository,
            ent_repo: IEntertainmentRepository,
            route_repo: IRouteRepository,
            travel_repo: ITravelRepository,
            user_repo: IUserRepository
        ):
        self.acc_repo = acc_repo
        self.city_repo = city_repo
        self.d_route_repo = d_route_repo
        self.ent_repo = ent_repo
        self.route_repo = route_repo
        self.travel_repo = travel_repo
        self.user_repo = user_repo
        

@dataclass
class Services:
    def __init__(self, acc_serv: AccommodationService, city_serv: CityService, 
            d_route_serv: DirectoryRouteService, ent_serv: EntertainmentService, 
            route_serv: RouteService, travel_serv: TravelService, user_serv: UserService, auth_serv: AuthService):
        self.acc_serv = acc_serv
        self.city_serv = city_serv
        self.d_route_serv = d_route_serv
        self.ent_serv = ent_serv
        self.route_serv = route_serv
        self.travel_serv = travel_serv
        self.user_serv = user_serv
        self.auth_serv = auth_serv


@dataclass
class Controllers:
    def __init__(self, acc_contr: AccommodationController, route_contr: RouteController, 
            ent_contr: EntertainmentController, travel_contr: TravelController, user_contr: UserController, 
            d_route_contr: DirectoryRouteController, city_contr: CityController):
        self.acc_contr = acc_contr
        self.city_contr = city_contr
        self.route_contr = route_contr
        self.d_route_contr = d_route_contr
        self.ent_contr = ent_contr
        self.travel_contr = travel_contr
        self.user_contr = user_contr


class ServiceLocator:
    def __init__(self, repositories: Repositories, services: Services, controllers: Controllers):
        self.repositories = repositories
        self.services = services
        self.controllers = controllers

    def get_acc_repo(self) -> IAccommodationRepository:
        return self.repositories.acc_repo

    def get_city_repo(self) -> ICityRepository:
        return self.repositories.city_repo

    def get_d_route_repo(self) -> IDirectoryRouteRepository:
        return self.repositories.d_route_repo

    def get_ent_repo(self) -> IEntertainmentRepository:
        return self.repositories.ent_repo

    def get_route_repo(self) -> IRouteRepository:
        return self.repositories.route_repo

    def get_travel_repo(self) -> ITravelRepository:
        return self.repositories.travel_repo

    def get_user_repo(self) -> IUserRepository:
        return self.repositories.user_repo

    def get_acc_serv(self) -> AccommodationService:
        return self.services.acc_serv

    def get_city_serv(self) -> CityService:
        return self.services.city_serv

    def get_d_route_serv(self) -> DirectoryRouteService:
        return self.services.d_route_serv

    def get_ent_serv(self) -> EntertainmentService:
        return self.services.ent_serv

    def get_route_serv(self) -> RouteService:
        return self.services.route_serv

    def get_travel_serv(self) -> TravelService:
        return self.services.travel_serv

    def get_user_serv(self) -> UserService:
        return self.services.user_serv

    def get_auth_serv(self) -> AuthService:
        return self.services.auth_serv

    def get_acc_contr(self) -> AccommodationController:
        return self.controllers.acc_contr

    def get_city_contr(self) -> CityController:
        return self.controllers.city_contr

    def get_route_contr(self) -> RouteController:
        return self.controllers.route_contr
    
    def get_d_route_contr(self) -> DirectoryRouteController:
        return self.controllers.d_route_contr

    def get_ent_contr(self) -> EntertainmentController:
        return self.controllers.ent_contr

    def get_travel_contr(self) -> TravelController:
        return self.controllers.travel_contr

    def get_user_contr(self) -> UserController:
        return self.controllers.user_contr


async def get_sessionmaker(max_retries: int = 5, delay: int = 2) -> Any: 
    global _async_session_maker
    if _async_session_maker is not None:
        return _async_session_maker
    engine = create_async_engine(
        settings.DATABASE_URL_ASYNC,
        connect_args={
            "server_settings": {
                "search_path": "travel_db" 
            }
        },
        echo=True,
        pool_pre_ping=True
    )   
    for attempt in range(max_retries):
        try:
            return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        except OperationalError as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Повторная попытка подключения через {delay} секунд...")
                await asyncio.sleep(delay)
            else:
                raise RuntimeError("Не удалось подключиться к базе данных после нескольких попыток.")
    return None


async def get_service_locator() -> ServiceLocator:
    global _mongo_client, _async_session_maker
    
    db_type = "mongo" if "mongo" in settings.DATABASE_URL_ASYNC else "postgres"
    
    if db_type == "mongo":
        if _mongo_client is None:
            _mongo_client = AsyncIOMotorClient(settings.DATABASE_URL_ASYNC)
        mongo_client: AsyncIOMotorClient[Any] = _mongo_client
        m_city_repo: ICityRepository = MongoCityRepository(mongo_client)
        m_d_route_repo: IDirectoryRouteRepository = MongoDirectoryRouteRepository(mongo_client, m_city_repo)
        m_acc_repo: IAccommodationRepository = MongoAccommodationRepository(mongo_client, m_city_repo)
        m_ent_repo: IEntertainmentRepository = MongoEntertainmentRepository(mongo_client, m_city_repo)
        m_user_repo: IUserRepository = MongoUserRepository(mongo_client)
        m_travel_repo: ITravelRepository = MongoTravelRepository(mongo_client, m_user_repo, m_ent_repo, m_acc_repo)
        m_route_repo: IRouteRepository = MongoRouteRepository(mongo_client, m_d_route_repo, m_travel_repo)

        acc_serv = AccommodationService(m_acc_repo)
        city_serv = CityService(m_city_repo)
        d_route_serv = DirectoryRouteService(m_d_route_repo)
        ent_serv = EntertainmentService(m_ent_repo)
        route_serv = RouteService(m_route_repo)
        travel_serv = TravelService(m_travel_repo)
        user_serv = UserService(m_user_repo)
        auth_serv = AuthService(m_user_repo)

        repositories = Repositories(m_acc_repo, m_city_repo, m_d_route_repo, m_ent_repo, m_route_repo, m_travel_repo, m_user_repo)
    else:
        if _async_session_maker is None:
            _async_session_maker = await get_sessionmaker()
        async with _async_session_maker() as session:
            city_repo: ICityRepository = CityRepository(session)
            d_route_repo: IDirectoryRouteRepository = DirectoryRouteRepository(session, city_repo)
            acc_repo: IAccommodationRepository = AccommodationRepository(session, city_repo)
            ent_repo: IEntertainmentRepository = EntertainmentRepository(session, city_repo)
            user_repo: IUserRepository = UserRepository(session)
            travel_repo: ITravelRepository = TravelRepository(session, user_repo, ent_repo, acc_repo)
            route_repo: IRouteRepository = RouteRepository(session, d_route_repo, travel_repo)

            repositories = Repositories(acc_repo, city_repo, d_route_repo, ent_repo, route_repo, travel_repo, user_repo)
        
        acc_serv = AccommodationService(acc_repo)
        city_serv = CityService(city_repo)
        d_route_serv = DirectoryRouteService(d_route_repo)
        ent_serv = EntertainmentService(ent_repo)
        route_serv = RouteService(route_repo)
        travel_serv = TravelService(travel_repo)
        user_serv = UserService(user_repo)
        auth_serv = AuthService(user_repo)
    
    city_contr = CityController(city_serv)
    route_contr = RouteController(route_serv, travel_serv, d_route_serv, user_serv, ent_serv, acc_serv) 
    d_route_contr = DirectoryRouteController(d_route_serv, city_serv)
    acc_contr = AccommodationController(acc_serv, city_serv)
    ent_contr = EntertainmentController(ent_serv, city_serv)
    travel_contr = TravelController(travel_serv, user_serv, ent_serv, acc_serv)
    user_contr = UserController(user_serv, auth_serv)

    services = Services(acc_serv, city_serv, d_route_serv, ent_serv, route_serv, travel_serv, user_serv, auth_serv)
    controllers = Controllers(acc_contr, route_contr, ent_contr, travel_contr, user_contr, 
                                                                                d_route_contr, city_contr)
    
    return ServiceLocator(repositories, services, controllers)