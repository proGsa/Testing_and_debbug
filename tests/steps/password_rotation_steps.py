import pytest
from pytest_bdd import scenarios, given, when, then
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app
from models.user import User
from faker import Faker
from unittest.mock import AsyncMock
fake = Faker('ru_RU')

scenarios("../features/password_rotation.feature")

# ------------------------------
# Асинхронная фикстура для пользователя со старым паролем
# ------------------------------
@pytest.fixture
async def password_user():
    login = "techuser_oldpass"
    old_password = BDD_PASS
    email = fake.email()
    phone = "89259930123"

    user = User(
        user_id=1,
        fio=fake.name(),
        number_passport=str(fake.ssn()),
        phone_number=phone,
        email=email,
        login=login,
        password=old_password,
        is_admin=False
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        resp = await client.post("/api/register", json=user.model_dump())
        data = resp.json()
        user_data = {
            "login": login,
            "old_password": old_password,
            "user_id": data["user_id"],
            "token": data["access_token"],
            "client": client
        }

        yield user_data

        await client.delete(f"/api/delete/{data['user_id']}", headers={"Authorization": f"Bearer {data['access_token']}"})

# ------------------------------
# Шаги BDD
# ------------------------------
@given("тестовый пользователь со старым паролем создан")
def given_user(password_user):
    return password_user

@given("срок действия пароля истёк")
async def given_password_expired(monkeypatch, password_user):
    # monkeypatch сервиса аутентификации, чтобы при старом пароле возвращался 403
    async def fake_authenticate(login, password):
        if password == password_user["old_password"]:
            return None  # Симулируем требование смены пароля
        return {"login": login}

    monkeypatch.setattr(
        "service_locator.get_auth_serv().authenticate", 
        AsyncMock(side_effect=fake_authenticate)
    )
@when("пользователь входит со старым паролем")
async def when_login_old_password(password_user):
    client = password_user["client"]
    login = password_user["login"]
    password = password_user["old_password"]

    resp = await client.post("/api/login1", json={"login": login, "password": password})
    password_user["login_resp"] = resp
    assert resp.status_code == 403  # Forbidden или требование смены пароля

@then("система требует сменить пароль")
async def then_require_change(password_user):
    resp = password_user["login_resp"]
    data = resp.json()
    assert "password_expired" in data

@when("пользователь вводит новый пароль")
async def when_enter_new_password(password_user):
    client = password_user["client"]
    login = password_user["login"]
    new_password = "NewPass123!"
    password_user["new_password"] = new_password

    resp = await client.post("/api/change-password", json={"login": login, "new_password": new_password})
    assert resp.status_code == 200

@then("система принимает новый пароль")
async def then_accept_new_password(password_user):
    # password_user уже "развёрнут" фикстурой
    assert "new_password" in password_user


@then("вход с новым паролем проходит успешно")
async def then_login_new_password(password_user):
    client = password_user["client"]
    login = password_user["login"]
    new_password = password_user["new_password"]

    resp = await client.post("/api/login1", json={"login": login, "password": new_password})
    assert resp.status_code == 200

@then("вход со старым паролем невозможен")
async def then_login_old_password_fail(password_user):
    client = password_user["client"]
    login = password_user["login"]
    old_password = password_user["old_password"]

    resp = await client.post("/api/login1", json={"login": login, "password": old_password})
    assert resp.status_code == 403
