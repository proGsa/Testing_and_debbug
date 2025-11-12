from __future__ import annotations

import logging

# from contextlib import AsyncGenerator
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from logger import setup_logging
from routers.accommodation import accommodation_router
from routers.city import city_router
from routers.d_route import d_router
from routers.entertainment import entertainment_router
from routers.route import router
from routers.travel import travel_router
from routers.user import user_router


templates = Jinja2Templates(directory="templates")

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Запуск приложения")
    yield
    logger.info("Завершение работы приложения")


app = FastAPI(lifespan=lifespan)
routers = [
    router,
    d_router,
    city_router,
    user_router,
    accommodation_router,
    travel_router,
    entertainment_router,
]

for r in routers:
    app.include_router(r)


@app.get("/", response_class=HTMLResponse)
async def serve_main_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("register.html", {"request": request})


@app.exception_handler(Exception)
async def handle_exceptions(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Ошибка при обработке запроса: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "OK"}
