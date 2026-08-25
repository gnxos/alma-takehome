from sqlalchemy import Engine, inspect, text

from app.database.base import Base
from app.database.session import engine
from app.services.reference_numbers import generate_reference_number


def init_db(target_engine: Engine | None = None) -> None:
    """Create current tables and upgrade the legacy SQLite lead schema."""
    from app.models import Lead  # noqa: F401

    database_engine = target_engine or engine
    Base.metadata.create_all(bind=database_engine)

    # The ALTER TABLE statements below are a dev convenience for upgrading an
    # existing local SQLite file in place, and use bare, length-less VARCHAR
    # (fine for SQLite, invalid on MySQL). Production points at a fresh
    # MySQL database, whose "leads" table is created directly above by
    # create_all() with the model's real (length-bound) column types, so
    # there's nothing to upgrade there.
    if database_engine.dialect.name != "sqlite":
        return

    inspector = inspect(database_engine)
    if "leads" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("leads")}
    
    new_columns = [
        ("company", "VARCHAR"),
        ("linkedin", "VARCHAR"),
        ("phone", "VARCHAR"),
        ("country_of_birth", "VARCHAR"),
        ("visas_of_interest", "VARCHAR"),
        ("visa_sponsor", "VARCHAR"),
        ("message", "VARCHAR"),
        ("how_did_you_hear", "VARCHAR"),
        ("referral_code", "VARCHAR"),
        ("prospect_email_status", "VARCHAR DEFAULT 'PENDING'"),
        ("attorney_email_status", "VARCHAR DEFAULT 'PENDING'"),
    ]

    with database_engine.begin() as connection:
        if "reference_number" not in columns:
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

        for col_name, col_type in new_columns:
            if col_name not in columns:
                connection.execute(
                    text(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")
                )
