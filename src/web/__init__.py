from pydantic import BaseModel

from ..utils.enums import RequestStatus


class RequestResponse(BaseModel):
    status: RequestStatus
    message: str | None = None
