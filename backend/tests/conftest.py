from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

_tmp_dir = tempfile.mkdtemp(prefix="ecorestore_test_")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{Path(_tmp_dir, 'test.db').as_posix()}")
os.environ.setdefault("CHROMA_PERSIST_DIRECTORY", str(Path(_tmp_dir, "chroma")))
os.environ.setdefault(
    "SEED_SOURCES_DIR", str(BACKEND_DIR.parent / "knowledge_base" / "seed_sources")
)
os.environ.setdefault("LLM_PROVIDER", "none")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.ingestion import run_full_ingestion  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_full_ingestion(db)
    finally:
        db.close()
    yield


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


SUNDARBANS_SAMPLE = {
    "location_name": "Sundarbans-adjacent coastal area",
    "latitude": 21.95,
    "longitude": 88.75,
    "ecosystem_type": "mangrove",
    "land_use": "degraded mangrove edge",
    "soil_organic_carbon_percent": 0.4,
    "soil_ph": 7.8,
    "soil_moisture_percent": 18,
    "soil_salinity": "high",
    "rainfall_pattern": "irregular",
    "temperature_trend": "rising",
    "habitat_fragmentation": "high",
    "human_impact": ["aquaculture expansion", "plastic pollution"],
    "species_observations": "low bird and pollinator activity",
}
