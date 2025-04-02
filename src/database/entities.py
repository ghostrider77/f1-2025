from datetime import date, datetime, timedelta
from sqlalchemy import Engine, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .enums import RaceFormat


class Base(DeclarativeBase):
    pass


def create_all_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


class Driver(Base):
    __tablename__ = "driver"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)

    name: Mapped[str] = mapped_column(String(128), unique=True)
    country: Mapped[str] = mapped_column(String(64))

    results: Mapped[list["Result"]] = relationship(back_populates="driver", cascade="all, delete-orphan")


class Constructor(Base):
    __tablename__ = "constructor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)

    name: Mapped[str] = mapped_column(String(128), unique=True)

    results: Mapped[list["Result"]] = relationship(back_populates="constructor", cascade="all, delete-orphan")


class Race(Base):
    __tablename__ = "race"

    __table_args__ = (UniqueConstraint("name", "race_format"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)

    name: Mapped[str] = mapped_column(String(64))
    circuit_name: Mapped[str | None] = mapped_column(String(64))
    circuit_location: Mapped[str | None] = mapped_column(String(64))
    country: Mapped[str | None] = mapped_column(String(64))
    race_date: Mapped[date]
    race_format: Mapped[RaceFormat] = mapped_column(Enum(RaceFormat, native_enum=False, length=24))

    results: Mapped[list["Result"]] = relationship(back_populates="race", cascade="all, delete-orphan")

    @hybrid_property
    def prediction_deadline(self) -> date:
        return self.race_date - timedelta(days=2)


class Result(Base):
    __tablename__ = "result"

    __table_args__ = (UniqueConstraint("driver_id", "race_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)

    driver_id: Mapped[int] = mapped_column(ForeignKey("driver.id"))
    constructor_id: Mapped[int] = mapped_column(ForeignKey("constructor.id"))
    race_id: Mapped[int] = mapped_column(ForeignKey("race.id"))

    position: Mapped[int]
    points: Mapped[float]

    driver: Mapped["Driver"] = relationship(back_populates="results")
    constructor: Mapped["Constructor"] = relationship(back_populates="results")
    race: Mapped["Race"] = relationship(back_populates="results")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)

    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    password: Mapped[bytes]

    predictions: Mapped[list["Prediction"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "prediction"

    __table_args__ = (UniqueConstraint("user_id", "race_id", "driver_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    race_id: Mapped[int] = mapped_column(ForeignKey("race.id", onupdate="CASCADE", ondelete="CASCADE"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("driver.id", onupdate="CASCADE", ondelete="CASCADE"))

    prediction_time_utc: Mapped[datetime]
    position: Mapped[int]

    user: Mapped["User"] = relationship(back_populates="predictions")
