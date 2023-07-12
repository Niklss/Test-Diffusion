from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from router import kafka_router

app = FastAPI()

app.include_router(kafka_router, prefix="/api", tags=["diffusers"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title="Test api", version="2.5.0",
                                 description="This API allow to run stable diffusion", routes=app.routes, )
    openapi_schema["info"]["x-logo"] = {"url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
