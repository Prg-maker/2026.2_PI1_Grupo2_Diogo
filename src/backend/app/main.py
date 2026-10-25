from fastapi import FastAPI
from app.core.config import settings
from app.core.database import test_database_connection
from app.routes import sessions, telemetry
from fastapi.middleware.cors import CORSMiddleware
import os


app = FastAPI(
    title="Micromouse API",
    version="0.1.0",
)

app.include_router(sessions.router, prefix="/api")
app.include_router(telemetry.router, prefix="/api")
app.include_router(telemetry.websocket_router)

origens = os.getenv("CORS_ORIGINS", "*").split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Micromouse API funcionando"
    }


@app.get("/health")
def health():
    try:
        test_database_connection()

        return {
            "status": "ok",
            "database": "connected",
        }

    except Exception as error:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(error),
        }
