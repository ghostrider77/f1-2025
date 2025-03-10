import functools as ft

from collections import defaultdict
from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Callable, Concatenate, ParamSpec, TypeVar

from .distance import calc_distance
from ..database.engine import DBEngine
from ..database.enums import RaceFormat
from ..database.entities import Constructor, Driver, Prediction, Race, Result, User
from ..utils.auth import hash_password, is_password_valid
from ..utils.enums import RequestStatus
from ..web import RequestResponse
from ..web.participants.models import DriverModel, PredictionModel, RaceModel, ResultModel, ScoreModel
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

    @_with_engine
    def make_prediction(self, session: Session, prediction: PredictionModel) -> RequestResponse:
        if (user_entity := self._retrieve_user(prediction.username)) is None:
            error_msg = f"User(username={prediction.username}) is not found."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        if not is_password_valid(prediction.password, stored_password=user_entity.password):
            error_msg = f"Failed to authenticate User(username={prediction.username})."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        if (race_entity := self._retrieve_race(prediction.race_name, prediction.race_format)) is None:
            error_msg = f"Race(name={prediction.race_name}, format={prediction.race_format}) is not found."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        prediction_time = datetime.now(tz=UTC)
        if prediction_time.date() > race_entity.prediction_deadline:
            error_msg = f"Prediction deadline {race_entity.prediction_deadline} is already passed."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        prediction_entities = []
        for ix, driver_name in enumerate(prediction.drivers, start=1):
            if (driver := self._retrieve_driver(driver_name)) is None:
                error_msg = f"Unknown driver {driver_name}."
                return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

            entity = Prediction(
                race_id=race_entity.id, driver_id=driver.id, position=ix, prediction_time_utc=prediction_time
            )
            prediction_entities.append(entity)

        try:
            session.add(user_entity)
            user_entity.predictions.extend(prediction_entities)
            session.commit()
            return RequestResponse(status=RequestStatus.SUCCESS)

        except IntegrityError:
            session.rollback()
            error_msg = "Failed to add predictions, maybe already predicted this race."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

    def authenticate(self, username: str, password: str) -> bool:
        if (user_entity := self._retrieve_user(username)) is None:
            return False

        return is_password_valid(password, stored_password=user_entity.password)

    @_with_engine
    def delete_prediction(self, session: Session, username: str, race_name: str, race_format: RaceFormat) -> None:
        query = (select(Prediction)
                 .join(User)
                 .join(Race)
                 .where(User.username == username,
                        Race.name == race_name,
                        Race.race_format == race_format))  # fmt: skip

        predictions = session.execute(query).scalars().all()
        for prediction in predictions:
            session.delete(prediction)

        session.commit()

    @_with_engine
    def add_result(self, session: Session, result: ResultModel) -> RequestResponse:
        if (race_entity := self._retrieve_race(result.race_name, result.race_format)) is None:
            error_msg = f"Race(name={result.race_name}, format={result.race_format}) is not found."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        if (driver_entity := self._retrieve_driver(result.driver)) is None:
            error_msg = f"Driver(name={result.driver}) is not found."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        if (constructor_entity := self._retrieve_constructor(result.constructor)) is None:
            error_msg = f"Constructor(name={result.driver}) is not found."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

        race_result = Result(
            driver_id=driver_entity.id,
            constructor_id=constructor_entity.id,
            position=result.position,
            points=result.points,
        )
        try:
            session.add(race_entity)
            race_entity.results.append(race_result)
            session.commit()
            return RequestResponse(status=RequestStatus.SUCCESS)

        except IntegrityError:
            session.rollback()
            error_msg = "Failed to add result to race."
            return RequestResponse(status=RequestStatus.FAILURE, message=error_msg)

    def calc_score(self, request: ScoreModel) -> float | None:
        if self._retrieve_race(request.race_name, request.race_format) is None:
            return None

        predicted_drivers = self._retrieve_predicted_drivers(request.username, request.race_name, request.race_format)
        point_scoring_drivers = self._retrieve_point_scorers(request.race_name, request.race_format)
        return calc_distance(predicted_drivers, point_scoring_drivers)

    def calc_total_score(self, username: str) -> float | None:
        races = self.get_races()

        scores = []
        for race in races:
            score_request = ScoreModel(username=username, race_name=race.name, race_format=race.race_format)
            if (score := self.calc_score(score_request)) is not None:
                scores.append(score)

        if not scores:
            return None

        return sum(scores)

    def get_standings(self) -> list[tuple[str, float]]:
        users = self._retrieve_users()

        scores = []
        for user in users:
            if (score := self.calc_total_score(user.username)) is not None:
                scores.append((user.username, score))

        return sorted(scores, key=lambda x: x[1])

    def get_race_predictions(self, race_name: str, race_format: RaceFormat) -> dict[str, list[str]]:
        return self._retrieve_predictions(race_name, race_format)

    @_with_engine
    def get_races(self, session: Session) -> list[RaceModel]:
        query = select(Race).order_by(Race.race_date)
        result = session.execute(query).scalars().all()

        return list(map(RaceModel.model_validate, result))

    @_with_engine
    def get_drivers(self, session: Session) -> list[DriverModel]:
        query = select(Driver).order_by(Driver.id)
        result = session.execute(query).scalars().all()

        return list(map(DriverModel.model_validate, result))

    @_with_engine
    def _retrieve_constructor(self, session: Session, name: str) -> Constructor | None:
        query = select(Constructor).where(Constructor.name == name)
        return session.execute(query).scalars().first()

    @_with_engine
    def _retrieve_driver(self, session: Session, name: str) -> Driver | None:
        query = select(Driver).where(Driver.name == name)
        return session.execute(query).scalars().first()

    @_with_engine
    def _retrieve_race(self, session: Session, race_name: str, race_format: RaceFormat) -> Race | None:
        query = select(Race).where(Race.name == race_name, Race.race_format == race_format)
        return session.execute(query).scalars().first()

    @_with_engine
    def _retrieve_predicted_drivers(
        self,
        session: Session,
        username: str,
        race_name: str,
        race_format: RaceFormat,
    ) -> list[str]:
        query = (select(Driver.name)
                 .join(Prediction)
                 .join(User)
                 .join(Race)
                 .where(User.username == username,
                        Race.name == race_name,
                        Race.race_format == race_format)
                 .order_by(Prediction.position))  # fmt: skip

        return list(session.execute(query).scalars().all())

    @_with_engine
    def _retrieve_point_scorers(self, session: Session, race_name: str, race_format: RaceFormat) -> list[str]:
        query = (select(Driver.name)
                 .join(Result)
                 .join(Race)
                 .where(Race.name == race_name,
                        Race.race_format == race_format,
                        Result.points > 0.0)
                 .order_by(Result.position))  # fmt: skip

        return list(session.execute(query).scalars().all())

    @_with_engine
    def _retrieve_predictions(self, session: Session, race_name: str, race_format: RaceFormat) -> dict[str, list[str]]:
        query = (select(User.username, Driver.name)
                 .join(Prediction, Prediction.user_id == User.id)
                 .join(Driver)
                 .join(Race)
                 .where(Race.name == race_name,
                        Race.race_format == race_format)
                 .order_by(User.username, Prediction.position))  # fmt: skip

        result_rows = session.execute(query).all()
        result = defaultdict(list)
        for row in result_rows:
            result[row.username].append(row.name)

        return dict(result)

    @_with_engine
    def _retrieve_user(self, session: Session, username: str) -> User | None:
        query = select(User).where(User.username == username)
        return session.execute(query).scalars().first()

    @_with_engine
    def _retrieve_users(self, session: Session) -> list[User]:
        return list(session.execute(select(User)).scalars().all())
