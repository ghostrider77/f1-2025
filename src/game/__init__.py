from .dbops import DBOperations
from ..database.engine import DBEngine
from ..configs.config import SERVICE_CONFIG

db_engine = DBEngine(**SERVICE_CONFIG.database.model_dump())
db_ops = DBOperations(db_engine=db_engine)
