from fastapi import APIRouter

from .models import UserModel
from .. import RequestResponse
from ...dependencies import DBDependency

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.post("/create")
def create_user(registration: UserModel, db: DBDependency) -> RequestResponse:
    return db.create_user(registration)
