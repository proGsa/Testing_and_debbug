from __future__ import annotations


import allure
import httpx
import pytest

from faker import Faker


fake = Faker("ru_RU")
TMP = 200


@allure.feature("E2E City Management")
@allure.story("Login and add city flow")
class TestCityManagementE2E:
    @pytest.mark.asyncio
    async def test_login_and_add_city_api(self) -> None:
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            with allure.step("Prepare login data"):
                login_data = {"login": "admin1", "password": "123!e5T78"}

            with allure.step("Send login request"):
                resp = await client.post("/api/login", json=login_data)
                assert resp.status_code == TMP
                token = resp.json().get("access_token")
                assert token

            headers = {"Authorization": f"Bearer {token}"}

            with allure.step("Create new city 'Сочи'"):
                try:
                    create_resp = await client.post(
                        "/api/cities", json={"name": "Сочи"}, headers=headers
                    )
                except:
                    create_resp = await client.post(
                        "/api/cities", data={"name": "Сочи"}, headers=headers
                    )

                print(f"Create city response: {create_resp.status_code}")
                assert create_resp.status_code in (200, 201)

            with allure.step("Verify city via HTML page"):
                list_resp = await client.get("/city.html", headers=headers)
                print(f"HTML page status: {list_resp.status_code}")
                print(f"HTML content length: {len(list_resp.text)}")

                assert list_resp.status_code == TMP
                assert "Сочи" in list_resp.text
