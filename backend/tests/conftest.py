import shutil
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core import config
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.services import email_validation


@pytest.fixture(autouse=True)
def mock_dns_lookup(monkeypatch):
    """Default all test domains to "has mail exchanger" so tests don't hit
    real DNS. Individual tests can monkeypatch this again to test rejection."""
    monkeypatch.setattr(email_validation, "domain_has_mail_exchanger", lambda domain: True)


@pytest.fixture()
def client():
    tmp_dir = Path(tempfile.mkdtemp())
    db_path = tmp_dir / "test.db"
    config.UPLOAD_DIR = tmp_dir / "uploads"
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        # Most tests exercise the protected internal-dashboard endpoints, so
        # log in by default; tests of the auth flow itself (or of the public
        # create-lead endpoint) clear/ignore this cookie as needed.
        login_response = test_client.post(
            "/login",
            json={"email": config.ATTORNEY_EMAIL, "password": config.ATTORNEY_PASSWORD},
        )
        assert login_response.status_code == 200
        yield test_client

    app.dependency_overrides.clear()
    shutil.rmtree(tmp_dir, ignore_errors=True)
