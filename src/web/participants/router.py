from fastapi import APIRouter

from .models import DriverModel, PredictionModel, RaceModel, ResultModel, ScoreModel
from .. import RequestResponse
from ...dependencies import DBDependency

router = APIRouter(prefix="/api/v1/participants", tags=["actors"])


@router.post("/create/constructor", include_in_schema=False)
def create_constructor(name: str, db: DBDependency) -> RequestResponse:
    return db.create_constructor(name)


@router.post("/create/driver", include_in_schema=False)
def create_driver(registration: DriverModel, db: DBDependency) -> RequestResponse:
    return db.create_driver(registration)


@router.post("/create/race", include_in_schema=False)
def create_race(registration: RaceModel, db: DBDependency) -> RequestResponse:
    return db.create_race(registration)


@router.post("/add/result", include_in_schema=False, response_model_exclude_none=True)
def add_result(result: ResultModel, db: DBDependency) -> RequestResponse:
    return db.add_result(result)


@router.get("/get/races")
def get_races(db: DBDependency) -> list[RaceModel]:
    return db.get_races()


@router.get("/get/drivers")
def get_drivers(db: DBDependency) -> list[DriverModel]:
    return db.get_drivers()


@router.post("/get/score")
def calc_score(request: ScoreModel, db: DBDependency) -> float | None:
    return db.calc_score(request)


@router.get("/get/totalscore/{username}")
def calc_total_score(username: str, db: DBDependency) -> float | None:
    return db.calc_total_score(username)


@router.get("/get/standings")
def get_standings(db: DBDependency) -> list[tuple[str, float]]:
    return db.get_standings()


@router.post("/make/prediction", response_model_exclude_none=True)
def make_prediction(prediction: PredictionModel, db: DBDependency) -> RequestResponse:
    return db.make_prediction(prediction)
