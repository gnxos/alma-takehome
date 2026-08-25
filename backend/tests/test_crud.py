import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud
from app.database import Base


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def _create(db_session, email="ada@example.com"):
    return crud.create_lead(
        db_session,
        first_name="Ada",
        last_name="Lovelace",
        email=email,
        resume_filename="resume.pdf",
        resume_path="/tmp/resume.pdf",
    )


def test_create_lead_retries_on_reference_number_collision(db_session, monkeypatch):
    values = iter(["INT-2026-0001", "INT-2026-0001", "INT-2026-0002"])
    monkeypatch.setattr(crud, "generate_reference_number", lambda: next(values))

    first = _create(db_session, email="a@example.com")
    second = _create(db_session, email="b@example.com")

    assert first.reference_number == "INT-2026-0001"
    assert second.reference_number == "INT-2026-0002"


def test_create_lead_gives_up_after_max_attempts(db_session, monkeypatch):
    monkeypatch.setattr(crud, "generate_reference_number", lambda: "INT-2026-0001")
    _create(db_session, email="a@example.com")

    with pytest.raises(RuntimeError):
        _create(db_session, email="b@example.com")


def test_get_lead_by_email_returns_most_recent(db_session):
    _create(db_session, email="dupe@example.com")
    second = _create(db_session, email="dupe@example.com")

    found = crud.get_lead_by_email(db_session, "dupe@example.com")
    assert found.id == second.id


def test_get_lead_by_id_or_reference(db_session):
    lead = _create(db_session)
    assert crud.get_lead_by_id_or_reference(db_session, lead.id).id == lead.id
    assert crud.get_lead_by_id_or_reference(db_session, lead.reference_number).id == lead.id
    assert crud.get_lead_by_id_or_reference(db_session, "nonexistent") is None
