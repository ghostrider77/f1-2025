import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator

from .configs.config import SERVICE_CONFIG
from .database.entities import create_all_tables
from .game import db_engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    create_all_tables(db_engine.engine())
    yield

    db_engine.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def ping() -> str:
    return f"Welcome! The server is running at {SERVICE_CONFIG.web.host}:{SERVICE_CONFIG.web.port}."


if __name__ == "__main__":
    uvicorn.run(app, host=SERVICE_CONFIG.web.host, port=SERVICE_CONFIG.web.port)
