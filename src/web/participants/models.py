from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from ...database.enums import RaceFormat


class DriverModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(max_length=128)
    country: str = Field(max_length=64)


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
    date: date
    race_format: RaceFormat
