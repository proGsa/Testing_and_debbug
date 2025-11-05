import re
import base64
import pytest
from pytest_bdd import scenarios, given, when, then
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app
from models.user import User
from faker import Faker
import os

fake = Faker('ru_RU')

scenarios("../features/authentication.feature")
BDD_PASS = os.environ.get("BDD_USER_PASS")

# ------------------------------
# Асинхронная фикстура для тестового пользователя
# ------------------------------
@pytest.fixture
async def test_user_2fa():
    login = "techuser_2fa"
    password = BDD_PASS
    email = fake.email()
    phone = "89261930112"

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

# ------------------------------
# Шаги BDD
# ------------------------------
@given("существует тестовый пользователь для 2FA")
async def given_user(test_user_2fa):
    # "await" нужен, чтобы получить словарь из async генератора
    user_data = await test_user_2fa.__anext__()
    return user_data

@when("пользователь выполняет первичный вход")
async def when_login(test_user_2fa):
    client = test_user_2fa["client"]
    login = test_user_2fa["login"]
    password = test_user_2fa["password"]

    resp = await client.post("/api/login1", json={"login": login, "password": password})
    assert resp.status_code == 200
    test_user_2fa["login_resp"] = resp

@then("на почту отправлен код 2FA")
async def then_email_code(test_user_2fa):
    import httpx  # Асинхронный клиент для MailHog
    client = test_user_2fa["client"]

    async with httpx.AsyncClient() as mail_client:
        resp = await mail_client.get("http://localhost:8025/api/v2/messages")
        items = resp.json().get("items", [])
        assert len(items) > 0

        last_email = items[0]
        body = last_email["Content"]["Body"]
        if last_email["Content"]["Encoding"] == "base64":
            body = base64.b64decode(body).decode("utf-8", errors="ignore")

        code = re.search(r"\b\d{6}\b", body).group(0)
        test_user_2fa["2fa_code"] = code

@when("пользователь вводит правильный код")
async def when_enter_code(test_user_2fa):
    client = test_user_2fa["client"]
    login = test_user_2fa["login"]
    code = test_user_2fa["2fa_code"]

    resp = await client.post("/api/login2", json={"login": login, "code": code})
    test_user_2fa["2fa_resp"] = resp

@then("система выдает действительный access_token")
async def then_access_token(test_user_2fa):
    resp = test_user_2fa["2fa_resp"]
    assert resp.status_code == 200
    assert "access_token" in resp.json()