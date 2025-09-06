import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_USER = os.environ.get("POSTGRES_USER")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_HOST = os.environ.get("POSTGRES_HOST")
DB_NAME = os.environ.get("POSTGRES_DB")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=1800)
Session = sessionmaker(bind=engine)


def ensure_table_exists(table_sql):
    """Ensure a table exists by executing the provided CREATE TABLE IF NOT EXISTS statement."""
    with engine.connect() as connection:
        connection.execute(text(table_sql))
        connection.commit()
