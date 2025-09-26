# tests/e2e/test_auth_e2e_simple.py
import pytest
import allure
import httpx
import os
from faker import Faker

fake = Faker('ru_RU')


@allure.feature("E2E City Management")
@allure.story("Login and add city flow")
class TestCityManagementE2E:
    @pytest.mark.asyncio
    async def test_login_and_add_city_api(self):
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        async with httpx.AsyncClient(base_url=base_url) as client:
            with allure.step("Prepare login data"):
                login_data = {"login": "admin1", "password": "123!e5T78"}

            with allure.step("Send login request"):
                resp = await client.post("/login", json=login_data)
                assert resp.status_code == 200
                token = resp.json().get("access_token")
                assert token

            headers = {"Authorization": f"Bearer {token}"}

            with allure.step("Create new city 'Сочи'"):
                create_resp = await client.post("/api/cities", data={"name": "Сочи"}, headers=headers)
                assert create_resp.status_code in (200, 201)

            with allure.step("Verify city in list"):
                list_resp = await client.get("/city.html", headers=headers)
                assert list_resp.status_code == 200
                assert "Сочи" in list_resp.text
