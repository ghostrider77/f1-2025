from sqlalchemy import Engine, create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Session
from typing import Any


class DBEngine:
    def __init__(
        self,
        driver: str,
        *,
        username: str | None,
        password: str | None,
        host: str | None,
        port: int | None,
        database: str,
        **kwargs: Any,
    ) -> None:
        url = URL.create(driver, username=username, password=password, host=host, port=port, database=database)
        connect_args = kwargs.pop("connect_args", {})
        if driver.startswith("postgresql"):
            connect_args = {**connect_args, "options": "-c timezone=utc"}

        self._engine = create_engine(url, connect_args=connect_args, **kwargs)
        self._sessionmaker = sessionmaker(self._engine)

    def engine(self) -> Engine:
        return self._engine

    def close(self) -> None:
        self._engine.dispose()

    def session(self) -> Session:
        return self._sessionmaker()
