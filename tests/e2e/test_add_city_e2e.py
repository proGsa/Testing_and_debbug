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
                resp = await client.post("/api/login", json=login_data)
                assert resp.status_code == 200
                token = resp.json().get("access_token")
                assert token

            headers = {"Authorization": f"Bearer {token}"}

            with allure.step("Create new city 'Сочи'"):
                create_resp = await client.post("/api/cities", data={"name": "Сочи"}, headers=headers)
                print(f"Create city response: {create_resp.status_code}")
                print(f"Create city body: {create_resp.text}")
                assert create_resp.status_code in (200, 201)

            with allure.step("Verify city via API first"):
                # Сначала проверим через API
                api_resp = await client.get("/api/cities", headers=headers)
                print(f"API cities response: {api_resp.status_code}")
                print(f"API cities body: {api_resp.text}")
                assert api_resp.status_code == 200
                cities_data = api_resp.json()
                print(f"Cities from API: {cities_data}")
                # Проверим, что город есть в API ответе
                city_names = [city.get('name') for city in cities_data]
                assert "Сочи" in city_names

            with allure.step("Verify city in list"):
                list_resp = await client.get("/city.html", headers=headers)
                print(f"HTML page status: {list_resp.status_code}")
                print(f"HTML content sample: {list_resp.text[:500]}...")  # Первые 500 символов
                assert list_resp.status_code == 200
                assert "Сочи" in list_resp.text