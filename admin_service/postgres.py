import logging
import os
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

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


def create_admin_table():
    """Create admin_data table if it doesn't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS admin_data (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_email VARCHAR(255) NOT NULL,
            admin_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        
        # Create index on user_email for faster queries
        create_index_query = """
        CREATE INDEX IF NOT EXISTS idx_admin_data_user_email 
        ON admin_data(user_email);
        """
        cursor.execute(create_index_query)
        conn.commit()
        
        logger.info("Admin data table created successfully")
        
    except psycopg2.Error as e:
        logger.error(f"Error creating admin data table: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def save_admin_data(user_email, admin_text, admin_time=None):
    """Save admin data to database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Parse admin_time if provided, otherwise use current time
        if admin_time:
            try:
                # Try to parse ISO format timestamp
                parsed_time = datetime.fromisoformat(admin_time.replace('Z', '+00:00'))
            except ValueError:
                # If parsing fails, use current time
                logger.warning(f"Invalid timestamp format: {admin_time}, using current time")
                parsed_time = datetime.now()
        else:
            parsed_time = datetime.now()
        
        insert_query = """
        INSERT INTO admin_data (date, user_email, admin_data)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        
        cursor.execute(insert_query, (parsed_time, user_email, admin_text))
        admin_id = cursor.fetchone()[0]
        conn.commit()
        
        logger.info(f"Admin data saved successfully with ID: {admin_id}")
        return admin_id
        
    except psycopg2.Error as e:
        logger.error(f"Error saving admin data: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_admin_data():
    """Get all admin data from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT id, date, user_email, admin_data, created_at
        FROM admin_data
        ORDER BY date DESC;
        """
        
        cursor.execute(query)
        admin_records = cursor.fetchall()
        
        # Convert to list of dictionaries
        result = []
        for admin_record in admin_records:
            result.append({
                "id": admin_record["id"],
                "date": admin_record["date"].isoformat() if admin_record["date"] else None,
                "user_email": admin_record["user_email"],
                "admin_data": admin_record["admin_data"],
                "created_at": admin_record["created_at"].isoformat() if admin_record["created_at"] else None
            })
        
        logger.info(f"Retrieved {len(result)} admin records")
        return result
        
    except psycopg2.Error as e:
        logger.error(f"Error getting admin data: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_admin_data_by_user(user_email):
    """Get admin data for a specific user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT id, date, user_email, admin_data, created_at
        FROM admin_data
        WHERE user_email = %s
        ORDER BY date DESC;
        """
        
        cursor.execute(query, (user_email,))
        admin_records = cursor.fetchall()
        
        # Convert to list of dictionaries
        result = []
        for admin_record in admin_records:
            result.append({
                "id": admin_record["id"],
                "date": admin_record["date"].isoformat() if admin_record["date"] else None,
                "user_email": admin_record["user_email"],
                "admin_data": admin_record["admin_data"],
                "created_at": admin_record["created_at"].isoformat() if admin_record["created_at"] else None
            })
        
        logger.info(f"Retrieved {len(result)} admin records for user {user_email}")
        return result
        
    except psycopg2.Error as e:
        logger.error(f"Error getting admin data for user {user_email}: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Initialize database on import
if __name__ == "__main__":
    create_admin_table() 