from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from ...database.enums import RaceFormat


class DeletePredictionModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    username: str
    password: str

    race_name: str
    race_format: RaceFormat


class DriverModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(max_length=128)
    country: str = Field(max_length=64)


class PredictionInfoModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    race_name: str
    race_format: RaceFormat


class PredictionModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    username: str
    password: str

    race_name: str
    race_format: RaceFormat
    drivers: list[str]

    @field_validator("drivers", mode="after")
    @classmethod
    def check_if_driver_list_is_unique(cls, drivers: list[str]) -> list[str]:
        unique_drivers = set(drivers)
        if len(unique_drivers) != len(drivers):
            raise ValueError("Driver list is not unique!")

        return drivers


class RaceModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    name: str = Field(max_length=64)
    circuit_name: str | None = Field(None, max_length=64)
    circuit_location: str | None = Field(None, max_length=64)
    country: str | None = Field(None, max_length=64)
    race_date: date = Field(alias="date")
    race_format: RaceFormat


class ResultModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    race_name: str
    race_format: RaceFormat
    driver: str
    constructor: str
    position: int = Field(ge=1)
    points: float = Field(0.0, ge=0.0)


class ScoreModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    username: str
    race_name: str
    race_format: RaceFormat
