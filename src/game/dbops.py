import functools as ft

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Callable, Concatenate, ParamSpec, TypeVar

from ..database.engine import DBEngine
from ..database.entities import User
from ..utils.auth import hash_password
from ..utils.enums import RequestStatus
from ..web import RequestResponse
from ..web.user.models import UserModel

P = ParamSpec("P")
R = TypeVar("R")
DB = TypeVar("DB", bound="DBOperations")


class DBOperations:
    def __init__(self, db_engine: DBEngine) -> None:
        self._db_engine = db_engine

    @staticmethod
    def _with_engine(func: Callable[Concatenate[DB, Session, P], R]) -> Callable[Concatenate[DB, P], R]:
        @ft.wraps(func)
        def wrapper(self: DB, /, *args: P.args, **kwargs: P.kwargs) -> R:
            with self._db_engine.session() as session:
                return func(self, session, *args, **kwargs)

        return wrapper

    @_with_engine
    def create_user(self, session: Session, registration: UserModel) -> RequestResponse:
        if (hashed_password := hash_password(registration.password)) is None:
            error_msg = "Password should be an ASCII-string with length between 8 and 256."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        user_entry = User(username=registration.username, password=hashed_password)
        try:
            session.add(user_entry)
            session.commit()
            return RequestResponse(status=RequestStatus.SUCCESS)

        except IntegrityError:
            session.rollback()
            error_msg = f"Could not create User({registration.username}), it is already registered."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)
