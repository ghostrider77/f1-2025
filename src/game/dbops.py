import functools as ft

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Callable, Concatenate, ParamSpec, TypeVar

from ..database.engine import DBEngine
from ..database.entities import Constructor, Driver, Race, User
from ..utils.auth import hash_password, is_password_valid
from ..utils.enums import RequestStatus
from ..web import RequestResponse
from ..web.participants.models import DriverModel, RaceModel
from ..web.user.models import UserModel, UserPasswordChangeModel

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
    def create_constructor(self, session: Session, name: str) -> RequestResponse:
        constructor_entry = Constructor(name=name)
        try:
            session.add(constructor_entry)
            session.commit()
            return RequestResponse(status=RequestStatus.SUCCESS)

        except IntegrityError:
            session.rollback()
            error_msg = f"Could not create Constructor({name}), it is already created."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

    @_with_engine
    def create_driver(self, session: Session, driver: DriverModel) -> RequestResponse:
        driver_entry = Driver(**driver.model_dump())
        try:
            session.add(driver_entry)
            session.commit()
            return RequestResponse(status=RequestStatus.SUCCESS)

        except IntegrityError:
            session.rollback()
            error_msg = f"Could not create Driver({driver.name}), it is already created."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

    @_with_engine
    def create_race(self, session: Session, race: RaceModel) -> RequestResponse:
        race_entry = Race(**race.model_dump())
        try:
            session.add(race_entry)
            session.commit()
            return RequestResponse(status=RequestStatus.SUCCESS)

        except IntegrityError:
            session.rollback()
            error_msg = f"Could not create Race({race.name}), it is already created."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

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

    @_with_engine
    def change_user_password(self, session: Session, update_request: UserPasswordChangeModel) -> RequestResponse:
        if (user_entity := self._retrieve_user(update_request.username)) is None:
            error_msg = f"Cannot change password. User(username={update_request.username}) is not found."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        if not is_password_valid(update_request.current_password, stored_password=user_entity.password):
            error_msg = f"Failed to authenticate User(username={update_request.username}). Password cannot be changed."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        if (hashed_password := hash_password(update_request.new_password)) is None:
            error_msg = "Password should be an ASCII-string with length between 8 and 256."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        session.add(user_entity)
        user_entity.password = hashed_password
        session.commit()
        return RequestResponse(status=RequestStatus.SUCCESS)

    def authenticate(self, username: str, password: str) -> bool:
        if (user_entity := self._retrieve_user(username)) is None:
            return False

        return is_password_valid(password, stored_password=user_entity.password)

    @_with_engine
    def get_races(self, session: Session) -> list[RaceModel]:
        query = select(Race).order_by(Race.date)
        result = session.execute(query).scalars().all()

        return list(map(RaceModel.model_validate, result))

    @_with_engine
    def get_drivers(self, session: Session) -> list[DriverModel]:
        query = select(Driver).order_by(Driver.id)
        result = session.execute(query).scalars().all()

        return list(map(DriverModel.model_validate, result))

    @_with_engine
    def _retrieve_user(self, session: Session, username: str) -> User | None:
        query = select(User).where(User.username == username)
        return session.execute(query).scalars().first()
