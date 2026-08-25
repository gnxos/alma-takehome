import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.repositories import leads as lead_repository


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
    return lead_repository.create(
        db_session,
        first_name="Ada",
        last_name="Lovelace",
        email=email,
        resume_filename="resume.pdf",
        resume_path="/tmp/resume.pdf",
    )


def test_create_lead_retries_on_reference_number_collision(db_session, monkeypatch):
    values = iter(["INT-2026-0001", "INT-2026-0001", "INT-2026-0002"])
    monkeypatch.setattr(
        lead_repository,
        "generate_reference_number",
        lambda: next(values),
    )

    first = _create(db_session, email="a@example.com")
    second = _create(db_session, email="b@example.com")

    assert first.reference_number == "INT-2026-0001"
    assert second.reference_number == "INT-2026-0002"


def test_create_lead_gives_up_after_max_attempts(db_session, monkeypatch):
    monkeypatch.setattr(
        lead_repository,
        "generate_reference_number",
        lambda: "INT-2026-0001",
    )
    _create(db_session, email="a@example.com")

    with pytest.raises(RuntimeError):
        _create(db_session, email="b@example.com")


def test_get_lead_by_email_returns_most_recent(db_session):
    _create(db_session, email="dupe@example.com")
    second = _create(db_session, email="dupe@example.com")

    found = lead_repository.get_by_email(db_session, "dupe@example.com")
    assert found.id == second.id


def test_list_leads_by_email_returns_every_match_newest_first(db_session):
    first = _create(db_session, email="shared@example.com")
    _create(db_session, email="different@example.com")
    second = _create(db_session, email="Shared@Example.com")

    found = lead_repository.list_by_email(db_session, " SHARED@example.com ")

    assert [lead.id for lead in found] == [second.id, first.id]


def test_get_lead_by_id_or_reference(db_session):
    lead = _create(db_session)
    assert lead_repository.get_by_id_or_reference(db_session, lead.id).id == lead.id
    assert (
        lead_repository.get_by_id_or_reference(db_session, lead.reference_number).id
        == lead.id
    )
    assert lead_repository.get_by_id_or_reference(db_session, "nonexistent") is None
