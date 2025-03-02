from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from ...database.enums import RaceFormat


class DriverModel(BaseModel):
    name: str = Field(max_length=128)
    nationality: str = Field(max_length=64)


class RaceModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(max_length=64)
    circuit_name: str = Field(max_length=64)
    circuit_location: str = Field(max_length=64)
    date: date
    race_format: RaceFormat
