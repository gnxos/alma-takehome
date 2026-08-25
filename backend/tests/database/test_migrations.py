import tempfile
from pathlib import Path

from sqlalchemy import create_engine, text

from app.database.migrations import init_db


def test_init_db_adds_reference_number_column_and_backfills():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_legacy.db"
        engine = create_engine(f"sqlite:///{db_path}")

        # Simulate legacy schema without reference_number
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE leads (
                        id VARCHAR PRIMARY KEY,
                        first_name VARCHAR NOT NULL,
                        last_name VARCHAR NOT NULL,
                        email VARCHAR NOT NULL,
                        resume_filename VARCHAR NOT NULL,
                        resume_path VARCHAR NOT NULL,
                        status VARCHAR NOT NULL,
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    INSERT INTO leads (id, first_name, last_name, email, resume_filename, resume_path, status)
                    VALUES ('test-id-1', 'Jane', 'Doe', 'jane@example.com', 'resume.pdf', '/path', 'PENDING')
                    """
                )
            )

        # Run init_db migration
        init_db(target_engine=engine)

        # Verify column added and populated
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT id, reference_number FROM leads "
                    "WHERE id='test-id-1'"
                )
            ).fetchone()
            assert result is not None
            assert result[0] == "test-id-1"
            assert result[1] is not None
            assert result[1].startswith("INT-")
