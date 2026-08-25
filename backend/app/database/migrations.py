from sqlalchemy import Engine, inspect, text

from app.database.base import Base
from app.database.session import engine
from app.services.reference_numbers import generate_reference_number


def init_db(target_engine: Engine | None = None) -> None:
    """Create current tables and upgrade the legacy SQLite lead schema."""
    from app.models import Lead  # noqa: F401

    database_engine = target_engine or engine
    Base.metadata.create_all(bind=database_engine)

    inspector = inspect(database_engine)
    if "leads" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("leads")}
    if "reference_number" in columns:
        return

    with database_engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE leads ADD COLUMN reference_number VARCHAR")
        )
        lead_ids = connection.execute(
            text("SELECT id FROM leads WHERE reference_number IS NULL")
        ).scalars()
        for lead_id in lead_ids:
            connection.execute(
                text(
                    "UPDATE leads SET reference_number = :reference_number "
                    "WHERE id = :lead_id"
                ),
                {
                    "reference_number": generate_reference_number(),
                    "lead_id": lead_id,
                },
            )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "ix_leads_reference_number ON leads (reference_number)"
            )
        )
