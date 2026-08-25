from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db(target_engine=None):
    from app.reference import generate_reference_number

    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
    inspector = inspect(eng)
    if "leads" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("leads")}
        if "reference_number" not in columns:
            with eng.begin() as conn:
                conn.execute(text("ALTER TABLE leads ADD COLUMN reference_number VARCHAR"))
                rows = conn.execute(
                    text("SELECT id FROM leads WHERE reference_number IS NULL")
                ).fetchall()
                for row in rows:
                    lead_id = row[0]
                    conn.execute(
                        text("UPDATE leads SET reference_number = :ref WHERE id = :id"),
                        {"ref": generate_reference_number(), "id": lead_id},
                    )
                try:
                    conn.execute(
                        text(
                            "CREATE UNIQUE INDEX IF NOT EXISTS ix_leads_reference_number ON leads (reference_number)"
                        )
                    )
                except Exception:
                    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
