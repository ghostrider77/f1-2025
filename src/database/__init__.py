from .engine import DBEngine
from ..configs.config import SERVICE_CONFIG

db_engine = DBEngine(**SERVICE_CONFIG.database.model_dump())
