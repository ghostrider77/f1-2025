from fastapi import APIRouter

from .models import DriverModel, RaceModel
from .. import RequestResponse
from ...dependencies import DBDependency

router = APIRouter(prefix="/api/v1/participants", tags=["actors"], include_in_schema=False)


@router.post("/create/constructor")
def create_constructor(name: str, db: DBDependency) -> RequestResponse:
    return db.create_constructor(name)


@router.post("/create/driver")
def create_driver(registration: DriverModel, db: DBDependency) -> RequestResponse:
    return db.create_driver(registration)


@router.post("/create/race")
def create_race(registration: RaceModel, db: DBDependency) -> RequestResponse:
    return db.create_race(registration)
