import re

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


USERNAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.]{1,62}[a-zA-Z0-9]$")


class UserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, extra="forbid", populate_by_name=True)

    username: str = Field(min_length=5, max_length=64, pattern=USERNAME_PATTERN)
    password: str = Field(max_length=256, repr=False)
