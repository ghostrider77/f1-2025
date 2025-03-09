from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from ...database.enums import RaceFormat


class DriverModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(max_length=128)
    country: str = Field(max_length=64)


class RaceModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    name: str = Field(max_length=64)
    circuit_name: str | None = Field(None, max_length=64)
    circuit_location: str | None = Field(None, max_length=64)
    country: str | None = Field(None, max_length=64)
    date: date
    race_format: RaceFormat
