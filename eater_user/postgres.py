import os
from databases import Database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "eater")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "eater")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Construct database URLs
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Async database for WebSocket operations
database = Database(ASYNC_DATABASE_URL)

# Log database connection info (without password)
logger.info(f"Database connection configured for {POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

# Simple database connection test
async def test_database_connection():
    """Test database connection using environment variables"""
    try:
        await database.connect()
        logger.info("Database connection successful")
        
        # Test a simple query
        result = await database.fetch_one("SELECT 1 as test")
        if result:
            logger.info("Database query test successful")
        else:
            logger.warning("Database query test failed")
            
        await database.disconnect()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        logger.error(f"Connection details: {POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
        logger.error(f"Environment variables: POSTGRES_USER={POSTGRES_USER}, POSTGRES_HOST={POSTGRES_HOST}, POSTGRES_DB={POSTGRES_DB}")
        return False



# Optimized query for autocomplete (WebSocket only)
async def autocomplete_query(query: str, limit: int, user_email: str):
    """
    Optimized autocomplete query for email search (WebSocket only)
    Excludes current user from results
    """
    # Sanitize and limit query length
    query = query.strip()[:100]
    if len(query) < 2:
        return []
    
    search_query = """
        SELECT email, register_date, last_activity
        FROM "user" 
        WHERE email ILIKE $1
        AND email != $5
        ORDER BY 
            CASE 
                WHEN email ILIKE $2 THEN 1  -- Exact prefix match
                WHEN email ILIKE $3 THEN 2  -- Domain match  
                ELSE 3                      -- Contains match
            END,
            length(email),                  -- Shorter emails first
            email                           -- Alphabetical consistency
        LIMIT $4
    """
    
    like_query = f"%{query}%"
    starts_with_query = f"{query}%"
    domain_query = f"%@{query}%"
    
    results = await database.fetch_all(
        search_query,
        like_query,
        starts_with_query,
        domain_query, 
        limit,
        user_email  # Exclude current user
    )
    
    users = [
        {
            "email": row["email"],
            "register_date": row["register_date"],
            "last_activity": row["last_activity"]
        }
        for row in results
    ]
    return users