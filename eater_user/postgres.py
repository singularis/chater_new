import os

from databases import Database

POSTGRES_USER = os.getenv("POSTGRES_USER", "eater")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "eater")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

ASYNC_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

database = Database(ASYNC_DATABASE_URL)


async def test_database_connection():
    try:
        await database.connect()
        result = await database.fetch_one("SELECT 1 as test")
        await database.disconnect()
        return bool(result)
    except Exception:
        return False


async def autocomplete_query(query: str, limit: int, user_email: str):
    try:
        query = query.strip()[:100]
        if len(query) < 2:
            return []

        search_query = """
            SELECT email, register_date, last_activity
            FROM "user" 
            WHERE email ILIKE :like_query
            AND email != :user_email
            ORDER BY 
                CASE 
                    WHEN email ILIKE :starts_with THEN 1
                    WHEN email ILIKE :domain_query THEN 2
                    ELSE 3
                END,
                length(email),
                email
            LIMIT :limit
        """

        like_query = f"%{query}%"
        starts_with_query = f"{query}%"
        domain_query = f"%@{query}%"

        results = await database.fetch_all(
            search_query,
            values={
                "like_query": like_query,
                "starts_with": starts_with_query,
                "domain_query": domain_query,
                "limit": limit,
                "user_email": user_email,
            },
        )

        users = []
        for row in results:
            user = {
                "email": row["email"],
                "register_date": (
                    row["register_date"].isoformat() if row["register_date"] else None
                ),
                "last_activity": (
                    row["last_activity"].isoformat() if row["last_activity"] else None
                ),
            }
            users.append(user)
        return users
    except Exception:
        raise


async def get_food_record_by_time(time: int, user_email: str):
    try:
        query = """
            SELECT dish_name, estimated_avg_calories, ingredients, total_avg_weight, contains, health_rating, food_health_level, image_id
            FROM public.dishes_day
            WHERE time = :time AND user_email = :user_email
            LIMIT 1
        """
        row = await database.fetch_one(
            query, values={"time": time, "user_email": user_email}
        )
        if not row:
            return None
        return {
            "dish_name": row["dish_name"],
            "estimated_avg_calories": row["estimated_avg_calories"],
            "ingredients": row["ingredients"],
            "total_avg_weight": row["total_avg_weight"],
            "contains": row["contains"],
            "health_rating": row["health_rating"],
            "food_health_level": row["food_health_level"],
            "image_id": row["image_id"],
        }
    except Exception:
        return None
