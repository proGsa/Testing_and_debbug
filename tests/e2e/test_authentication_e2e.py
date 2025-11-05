import re
import base64
import time
import requests
from faker import Faker
from httpx._transports.asgi import ASGITransport
import pytest
import httpx
from uuid import uuid4
from httpx import AsyncClient
from models.user import User

fake = Faker('ru_RU')

from main import app


@pytest.mark.asyncio
async def create_test_user(login: str, password: str, email: str, num: str):
    user = User(
        user_id = 1,
        fio=fake.name(),
        number_passport=str(fake.ssn()),
        phone_number=num,
        email=email,
        login=login,
        password=password,
        is_admin=False
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        resp_register = await client.post("/api/register", json=user.dict())
        assert resp_register.status_code == 200
        data = resp_register.json()
        access_token = data["access_token"]
        user_id = data["user_id"]
        return user_id, access_token

@pytest.mark.asyncio
async def delete_test_user(user_id: int, token: str):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        resp = await client.delete(f"/api/delete/{user_id}", headers={"Authorization": f"Bearer {token}"})
        print("DELETE response:", resp.status_code, resp.text, user_id)
        assert resp.status_code == 200

@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_2fa_email():
    login = "techuser_2fa"
    password = "Test123!"
    email = fake.email()
    num = "89261930112"
    user_id, token = await create_test_user(login, password, email, num)
    try:
         async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            resp_login = await client.post("/api/login1", json={"login": login, "password": password})
            assert resp_login.status_code == 200

            messages = requests.get("http://localhost:8025/api/v2/messages").json()
            assert len(messages["items"]) > 0
            last_email = messages["items"][0]
            body = base64.b64decode(last_email["Content"]["Body"]).decode("utf-8", errors="ignore")
            code = re.search(r"\b\d{6}\b", body).group(0)

            resp_2fa = await client.post("/api/login2", json={"login": login, "code": code})
            assert resp_2fa.status_code == 200
            assert "access_token" in resp_2fa.json()

    finally:
        await delete_test_user(user_id, token)


@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_login_attempt_limit():
    login = "techuser_limit"
    password = "Test123!"
    email = fake.email()
    num = "80261940112"
    user_id, token = await create_test_user(login, password, email, num)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            for _ in range(5):
                resp_fail = await client.post("/api/login1", json={"login": login, "password": "wrongpass"})
                assert resp_fail.status_code == 401

            resp_blocked = await client.post("/api/login1", json={"login": login, "password": password})
            assert resp_blocked.status_code == 403

    finally:
        await delete_test_user(user_id, token)


@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_recover_after_block():
    login = "techuser_block"
    password = "Test123!"
    email = fake.email()
    num = "89255930166"
    user_id, token = await create_test_user(login, password, email, num)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
            for _ in range(5):
                await client.post("/api/login1", json={"login": login, "password": "wrongpass"})

            resp_blocked = await client.post("/api/login1", json={"login": login, "password": password})
            assert resp_blocked.status_code == 403

            recover_resp = await client.post("/api/recover-password", json={"login": login})
            assert recover_resp.status_code == 200

            resp_login = await client.post("/api/login1", json={"login": login, "password": password})
            assert resp_login.status_code == 200

    finally:
        await delete_test_user(user_id, token)
