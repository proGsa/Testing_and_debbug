import pytest
from pytest_bdd import scenarios, given, when, then
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app
from models.user import User
from faker import Faker

fake = Faker('ru_RU')

scenarios("../features/recovery.feature")

@pytest.fixture
async def recover_user():
    login = "techuser_block"
    password = BDD_PASS
    email = fake.email()
    phone = "89255930166"

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

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
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


@given("тестовый пользователь создан для восстановления")
def given_user(recover_user):
    return recover_user

@when("пользователь 5 раз вводит неверный пароль")
async def when_wrong_password(recover_user):
    client = recover_user["client"]
    login = recover_user["login"]

    for _ in range(5):
        resp = await client.post("/api/login1", json={"login": login, "password": "wrongpass"})
        assert resp.status_code == 401

@when("система блокирует учетную запись")
async def when_blocked(recover_user):
    client = recover_user["client"]
    login = recover_user["login"]
    password = recover_user["password"]

    resp_blocked = await client.post("/api/login1", json={"login": login, "password": password})
    assert resp_blocked.status_code == 403

@when("пользователь запрашивает восстановление пароля")
async def when_recover_password(recover_user):
    client = recover_user["client"]
    login = recover_user["login"]

    recover_resp = await client.post("/api/recover-password", json={"login": login})
    assert recover_resp.status_code == 200

@then("система позволяет снова войти")
async def then_can_login(recover_user):
    client = recover_user["client"]
    login = recover_user["login"]
    password = recover_user["password"]

    resp_login = await client.post("/api/login1", json={"login": login, "password": password})
    assert resp_login.status_code == 200
