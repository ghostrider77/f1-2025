import re

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


USERNAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.]{1,62}[a-zA-Z0-9]$")


class UserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, extra="forbid", populate_by_name=True)

    username: str = Field(min_length=5, max_length=64, pattern=USERNAME_PATTERN)
    password: str = Field(max_length=256, repr=False)


class UserPasswordChangeModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    username: str
    current_password: str
    new_password: str = Field(min_length=8, max_length=256, repr=False)

    @field_validator("current_password", "new_password", mode="after")
    @classmethod
    def check_password_string(cls, password: str) -> str:
        if password.isascii():
            return password

        raise ValueError("Password should be an ASCII string with length between 8 and 256.")
