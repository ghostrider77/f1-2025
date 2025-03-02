from fastapi import Depends
from typing import Annotated

from .game import db_ops
from .game.dbops import DBOperations


def get_db() -> DBOperations:
    return db_ops


DBDependency = Annotated[DBOperations, Depends(get_db)]
