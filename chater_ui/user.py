import os
from datetime import datetime

from sqlalchemy import text

from postgres import Session, engine, ensure_table_exists

USER_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS "user" (
        email TEXT PRIMARY KEY,
        register_date TIMESTAMP,
        last_activity TIMESTAMP,
        model_tier TEXT,
        language TEXT
    )
"""

ensure_table_exists(USER_TABLE_SQL)


def update_user_activity(email, model_tier="cloud"):
    now = datetime.now()
    session = Session()
    try:
        result = session.execute(
            text('SELECT email FROM "user" WHERE email = :email'), {"email": email}
        ).fetchone()
        if result:
            session.execute(
                text('UPDATE "user" SET last_activity = :now WHERE email = :email'),
                {"now": now, "email": email},
            )
        else:
            session.execute(
                text(
                    'INSERT INTO "user" (email, register_date, last_activity, model_tier) VALUES (:email, :now, :now, :model_tier)'
                ),
                {"email": email, "now": now, "model_tier": model_tier},
            )
        session.commit()
    finally:
        session.close()


def set_user_language(email, language_code):
    language = (language_code or "en").strip().lower()
    if len(language) != 2:
        language = "en"

    now = datetime.now()
    session = Session()
    try:
        result = session.execute(
            text('SELECT email FROM "user" WHERE email = :email'), {"email": email}
        ).fetchone()
        if result:
            session.execute(
                text(
                    'UPDATE "user" SET language = :language, last_activity = :now WHERE email = :email'
                ),
                {"language": language, "now": now, "email": email},
            )
        else:
            session.execute(
                text(
                    'INSERT INTO "user" (email, register_date, last_activity, language) VALUES (:email, :now, :now, :language)'
                ),
                {"email": email, "now": now, "language": language},
            )
        session.commit()
        return language
    finally:
        session.close()


def get_user_language(email):
    session = Session()
    try:
        result = session.execute(
            text('SELECT language FROM "user" WHERE email = :email'), {"email": email}
        ).fetchone()
        language = result[0].strip().lower() if result and result[0] else "en"
        if len(language) != 2:
            language = "en"
        return language
    finally:
        session.close()

def get_user_model_tier(email):
    session = Session()
    try:
        result = session.execute(
            text('SELECT model_tier FROM "user" WHERE email = :email'), {"email": email}
        ).fetchone()
        model_tier = result[0].strip().lower() if result and result[0] else "cloud"
        if model_tier not in ["cloud", "local"]:
            model_tier = "cloud"
        return model_tier
    finally:
        session.close()