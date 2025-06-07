from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.etl.infrastructure.controller import router as patient_router

app = FastAPI()

app.include_router(patient_router)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Kannact demo",
        version="1.0.0",
        summary="Backend ETL, API and much more",
        description="Patients API allows to handle patients as well as biometric information",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
