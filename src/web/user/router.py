from fastapi import APIRouter

from .models import UserModel, UserPasswordChangeModel
from .. import RequestResponse
from ...dependencies import DBDependency

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.post("/create", response_model_exclude_none=True)
def create_user(registration: UserModel, db: DBDependency) -> RequestResponse:
    return db.create_user(registration)


@router.post("/change/password", response_model_exclude_none=True)
def change_password(request: UserPasswordChangeModel, db: DBDependency) -> RequestResponse:
    return db.change_user_password(request)
