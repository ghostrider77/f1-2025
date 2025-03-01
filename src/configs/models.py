from pydantic import BaseModel, ConfigDict


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    driver: str = "sqlite+pysqlite"
    username: str | None = None
    password: str | None = None
    host: str | None = None
    port: int | None = None
    database: str = ":memory:"


class WebConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    host: str = "0.0.0.0"
    port: int = 5000


class ServiceConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    database: DatabaseConfig
    web: WebConfig
