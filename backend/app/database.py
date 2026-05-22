from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# ── URL de conexión a PostgreSQL ──────────────
POSTGRES_USER     = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST     = os.getenv("POSTGRES_HOST")
POSTGRES_PORT     = os.getenv("POSTGRES_PORT")
POSTGRES_DB       = os.getenv("POSTGRES_DB")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# ── Base para los modelos ─────────────────────
Base = declarative_base()


# ── Patrón Singleton: DatabaseManager ────────
class DatabaseManager:
    """Garantiza una única instancia del motor y la fábrica de sesiones (Singleton)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._engine = create_engine(DATABASE_URL)
            cls._instance._session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls._instance._engine,
            )
        return cls._instance

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        return cls()

    @property
    def engine(self):
        return self._engine

    @property
    def session_local(self):
        return self._session_local


# ── Compatibilidad con el código existente ───
# Los routers y modelos importan estas variables directamente
_db_manager = DatabaseManager.get_instance()
engine       = _db_manager.engine
SessionLocal = _db_manager.session_local


# ── Dependencia para los endpoints ───────────
def get_db():
    db = DatabaseManager.get_instance().session_local()
    try:
        yield db
    finally:
        db.close()