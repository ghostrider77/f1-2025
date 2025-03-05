import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator

from src.web.participants.models import DriverModel, RaceModel
from . import PACKAGE_DIR
from .configs.config import SERVICE_CONFIG
from .database.entities import create_all_tables
from .game import db_engine, db_ops
from .utils.fileio import read_json_file
from .web.participants.router import router as actor_router
from .web.user.router import router as user_router


def initialize_database() -> None:
    folder = PACKAGE_DIR / "configs" / "data"
    for constructor in read_json_file(folder / "constructors.json"):
        db_ops.create_constructor(constructor)

    for line in read_json_file(folder / "drivers.json"):
        db_ops.create_driver(DriverModel.model_validate(line))

    for line in read_json_file(folder / "races.json"):
        db_ops.create_race(RaceModel.model_validate(line))


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    create_all_tables(db_engine.engine())
    initialize_database()
    yield

    db_engine.close()


app = FastAPI(lifespan=lifespan)
app.include_router(actor_router)
app.include_router(user_router)


@app.get("/")
def ping() -> str:
    return f"Welcome! The server is running at {SERVICE_CONFIG.web.host}:{SERVICE_CONFIG.web.port}."


if __name__ == "__main__":
    uvicorn.run(app, host=SERVICE_CONFIG.web.host, port=SERVICE_CONFIG.web.port)
