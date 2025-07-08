import os
from datetime import datetime
from sqlalchemy import text
from postgres import Session, ensure_table_exists

USER_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS "user" (
        email TEXT PRIMARY KEY,
        register_date TIMESTAMP,
        last_activity TIMESTAMP
    )
'''

ensure_table_exists(USER_TABLE_SQL)

def update_user_activity(email):
    now = datetime.now()
    session = Session()
    try:
        result = session.execute(
            text('SELECT email FROM "user" WHERE email = :email'),
            {"email": email}
        ).fetchone()
        if result:
            session.execute(
                text('UPDATE "user" SET last_activity = :now WHERE email = :email'),
                {"now": now, "email": email}
            )
        else:
            session.execute(
                text('INSERT INTO "user" (email, register_date, last_activity) VALUES (:email, :now, :now)'),
                {"email": email, "now": now}
            )
        session.commit()
    finally:
        session.close() 