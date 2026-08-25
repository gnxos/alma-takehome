from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATABASE_URL

# TODO (Production - MySQL on AWS RDS / Aurora):
# For production deployment with MySQL:
# 1. Set DATABASE_URL=mysql+pymysql://<user>:<password>@<rds-endpoint>:3306/<dbname>
# 2. Add connection pooling parameters:
#    engine = create_engine(
#        DATABASE_URL,
#        pool_size=10,
#        max_overflow=20,
#        pool_recycle=3600,
#        pool_pre_ping=True,
#    )
# 3. Use Alembic for automated database migrations in CI/CD.

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
