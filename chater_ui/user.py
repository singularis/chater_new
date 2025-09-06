import os
from datetime import datetime

from sqlalchemy import text

from postgres import Session, engine, ensure_table_exists

USER_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS "user" (
        email TEXT PRIMARY KEY,
        register_date TIMESTAMP,
        last_activity TIMESTAMP
    )
"""

ensure_table_exists(USER_TABLE_SQL)


def update_user_activity(email):
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
                    'INSERT INTO "user" (email, register_date, last_activity) VALUES (:email, :now, :now)'
                ),
                {"email": email, "now": now},
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
