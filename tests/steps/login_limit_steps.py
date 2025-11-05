import pytest
from pytest_bdd import scenarios, given, when, then
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app
from models.user import User
from faker import Faker

fake = Faker('ru_RU')
BDD_PASS = os.environ.get("BDD_USER_PASS")
scenarios("../features/login_limit.feature")

@pytest.fixture
async def test_user():
    login = "techuser_limit"
    password = BDD_PASS
    email = fake.email()
    phone = "80261940112"

    user = User(
        user_id=1,
        fio=fake.name(),
        number_passport=str(fake.ssn()),
        phone_number=phone,
        email=email,
        login=login,
        password=password,
        is_admin=False
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        resp = await client.post("/api/register", json=user.model_dump())
        data = resp.json()
        user_data = {
            "login": login,
            "password": password,
            "user_id": data["user_id"],
            "token": data["access_token"],
            "client": client
        }

        yield user_data 

        await client.delete(f"/api/delete/{data['user_id']}", headers={"Authorization": f"Bearer {data['access_token']}"})

@given("тестовый пользователь создан")
def given_user(test_user):
    return test_user

@when("пользователь 5 раз вводит неверный пароль")
async def when_wrong_password(test_user):
    client = test_user["client"]
    login = test_user["login"]

    for _ in range(5):
        resp = await client.post("/api/login1", json={"login": login, "password": "wrongpass"})
        assert resp.status_code == 401  # Unauthorized

@then("система блокирует дальнейший вход")
async def then_blocked_login(test_user):
    client = test_user["client"]
    login = test_user["login"]
    password = test_user["password"]

    resp = await client.post("/api/login1", json={"login": login, "password": password})
    assert resp.status_code == 403  # Forbidden / блокировка
