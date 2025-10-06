from contextlib import asynccontextmanager

from fastapi import FastAPI, Security
from dishka.integrations.fastapi import setup_dishka
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.routers.router import router
from app.adapters.routers.dependencies.dependencies import get_api_key
from app.infrastructure.di import create_container
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from app.settings import settings
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    global container
    container = create_container()
    setup_dishka(container=container, app=app)
    yield
    await container.close()

app = FastAPI(title="Secunda Тестовое Задание", summary="Тестовое задание для компании Secunda.\nСправочник организаций с авторизацией по ключу в хэдере",docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

container = create_container()
setup_dishka(container=container, app=app)

app.include_router(router, dependencies=[Security(get_api_key)])

@app.get("/docs", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

@app.get("/redoc", include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="redoc")

if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
