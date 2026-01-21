import logging
import os
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test@test.com")


# Database configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "database": os.getenv("POSTGRES_DB", "eater"),
    "user": os.getenv("POSTGRES_USER", "eater"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "port": os.getenv("DB_PORT", 5432),
}


def get_db_connection():
    """Get database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise


def create_feedback_table():
    """Create feedbacks table if it doesn't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS feedbacks (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_email VARCHAR(255) NOT NULL,
            feedback TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor.execute(create_table_query)
        conn.commit()

        create_index_query = """
        CREATE INDEX IF NOT EXISTS idx_feedbacks_user_email 
        ON feedbacks(user_email);
        """
        cursor.execute(create_index_query)
        conn.commit()

    except psycopg2.Error as e:
        logger.error(f"Error creating feedbacks table: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def save_feedback_data(user_email, feedback_text, feedback_time=None):
    """Save feedback data to database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if feedback_time:
            try:
                parsed_time = datetime.fromisoformat(
                    feedback_time.replace("Z", "+00:00")
                )
            except ValueError:
                logger.warning(
                    f"Invalid timestamp format: {feedback_time}, using current time"
                )
                parsed_time = datetime.now()
        else:
            parsed_time = datetime.now()

        insert_query = """
        INSERT INTO feedbacks (date, user_email, feedback)
        VALUES (%s, %s, %s)
        RETURNING id;
        """

        cursor.execute(insert_query, (parsed_time, user_email, feedback_text))
        feedback_id = cursor.fetchone()[0]
        conn.commit()

        return feedback_id

    except psycopg2.Error as e:
        logger.error(f"Error saving feedback data: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_feedback_data():
    """Get all feedback data from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
        SELECT id, date, user_email, feedback, created_at
        FROM feedbacks
        WHERE user_email != %s
        ORDER BY date DESC;
        """

        cursor.execute(query, (TEST_USER_EMAIL,))
        feedback_records = cursor.fetchall()

        result = []
        for feedback_record in feedback_records:
            result.append(
                {
                    "id": feedback_record["id"],
                    "date": (
                        feedback_record["date"].isoformat()
                        if feedback_record["date"]
                        else None
                    ),
                    "user_email": feedback_record["user_email"],
                    "feedback": feedback_record["feedback"],
                    "created_at": (
                        feedback_record["created_at"].isoformat()
                        if feedback_record["created_at"]
                        else None
                    ),
                }
            )

        return result

    except psycopg2.Error as e:
        logger.error(f"Error getting feedback data: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_feedback_data_by_user(user_email):
    """Get feedback data for a specific user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
        SELECT id, date, user_email, feedback, created_at
        FROM feedbacks
        WHERE user_email = %s
        ORDER BY date DESC;
        """

        cursor.execute(query, (user_email,))
        feedback_records = cursor.fetchall()

        result = []
        for feedback_record in feedback_records:
            result.append(
                {
                    "id": feedback_record["id"],
                    "date": (
                        feedback_record["date"].isoformat()
                        if feedback_record["date"]
                        else None
                    ),
                    "user_email": feedback_record["user_email"],
                    "feedback": feedback_record["feedback"],
                    "created_at": (
                        feedback_record["created_at"].isoformat()
                        if feedback_record["created_at"]
                        else None
                    ),
                }
            )

        return result

    except psycopg2.Error as e:
        logger.error(f"Error getting feedback data for user {user_email}: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_user_statistics():
    """Get comprehensive user statistics from food tracking tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM public.dishes_day;")
        total_dishes_scanned = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(DISTINCT user_email) FROM public.total_for_day;")
        total_users = cursor.fetchone()[0] or 0

        # Registered users from the main user table
        try:
            cursor.execute('SELECT COUNT(*) FROM public."user";')
            registered_users = cursor.fetchone()[0] or 0
        except Exception:
            # Fallback if table does not exist in some environments
            registered_users = 0

        cursor.execute("""
            SELECT COUNT(DISTINCT user_email) 
            FROM public.total_for_day 
            WHERE today::date >= CURRENT_DATE - INTERVAL '7 days';
        """)
        active_users_7_days = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(DISTINCT user_email) 
            FROM public.total_for_day 
            WHERE today::date >= CURRENT_DATE - INTERVAL '30 days';
        """)
        active_users_30_days = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT user_email
            FROM public.total_for_day 
            WHERE today::date >= CURRENT_DATE - 7
            GROUP BY user_email
            HAVING COUNT(DISTINCT today::date) >= 7
            ORDER BY user_email;
        """)
        constantly_active_7_days_emails = cursor.fetchall()
        constantly_active_7_days = len(constantly_active_7_days_emails)
        constantly_active_7_days_list = [
            row[0] for row in constantly_active_7_days_emails
        ]

        cursor.execute("""
            SELECT user_email
            FROM public.total_for_day 
            WHERE today::date >= CURRENT_DATE - 30
            GROUP BY user_email
            HAVING COUNT(DISTINCT today::date) >= 30
            ORDER BY user_email;
        """)
        constantly_active_30_days_emails = cursor.fetchall()
        constantly_active_30_days = len(constantly_active_30_days_emails)
        constantly_active_30_days_list = [
            row[0] for row in constantly_active_30_days_emails
        ]

        cursor.execute(
            "SELECT COUNT(*) FROM feedbacks WHERE user_email != %s;", (TEST_USER_EMAIL,)
        )
        total_feedback_records = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT ROUND(AVG(dish_count), 2) 
            FROM (
                SELECT COUNT(*) as dish_count 
                FROM public.dishes_day 
                GROUP BY user_email
            ) as user_dish_counts;
        """)
        avg_dishes_per_user = cursor.fetchone()[0] or 0

        statistics = {
            "total_users": total_users,
            "registered_users": registered_users,
            "active_users_7_days": active_users_7_days,
            "active_users_30_days": active_users_30_days,
            "constantly_active_7_days": constantly_active_7_days,
            "constantly_active_7_days_emails": constantly_active_7_days_list,
            "constantly_active_30_days": constantly_active_30_days,
            "constantly_active_30_days_emails": constantly_active_30_days_list,
            "total_dishes_scanned": total_dishes_scanned,
            "total_feedback_records": total_feedback_records,
            "avg_dishes_per_user": (
                float(avg_dishes_per_user) if avg_dishes_per_user else 0
            ),
        }

        return statistics

    except psycopg2.Error as e:
        logger.error(f"Error getting user statistics: {e}")
        return {
            "total_users": 0,
            "active_users_7_days": 0,
            "active_users_30_days": 0,
            "constantly_active_7_days": 0,
            "constantly_active_7_days_emails": [],
            "constantly_active_30_days": 0,
            "constantly_active_30_days_emails": [],
            "total_dishes_scanned": 0,
            "total_feedback_records": 0,
            "avg_dishes_per_user": 0,
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    create_feedback_table()
