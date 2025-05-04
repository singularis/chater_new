import logging
import os
import time

from sqlalchemy import (ARRAY, JSON, Column, Date, Float, ForeignKey, Integer,
                        PrimaryKeyConstraint, String, create_engine, text)
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Dishes(Base):
    __tablename__ = "dishes"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    ingredients = Column(ARRAY(String), nullable=False)
    contains = Column(JSON, nullable=False)
    user_email = Column(String, nullable=False)


class DishesDay(Base):
    __tablename__ = "dish_day"
    __table_args__ = (
        PrimaryKeyConstraint("dish_id", "date", "user_email"),
        {"schema": "public"},
    )

    dish_id = Column(Integer, ForeignKey("public.dishes.id"), nullable=False)
    date = Column(Date, nullable=False)
    user_email = Column(String, nullable=False)


class TotalForDay(Base):
    __tablename__ = "total_for_day"
    __table_args__ = (PrimaryKeyConstraint("date", "user_email"), {"schema": "public"})

    date = Column(Date, nullable=False)
    user_email = Column(String, nullable=False)
    total_calories = Column(Integer, nullable=False)
    ingredients = Column(ARRAY(String), nullable=False)
    dishes_of_day = Column(ARRAY(String), nullable=False)
    total_avg_weight = Column(Integer, nullable=False)
    contains = Column(JSON, nullable=False)


class Weight(Base):
    __tablename__ = "weights"
    __table_args__ = (PrimaryKeyConstraint("date", "user_email"), {"schema": "public"})

    date = Column(Date, nullable=False)
    user_email = Column(String, nullable=False)
    weight = Column(Float, nullable=False)


def create_tables():
    try:
        db_user = os.environ.get("POSTGRES_USER")
        db_password = os.environ.get("POSTGRES_PASSWORD")
        db_host = os.environ.get("POSTGRES_HOST")
        db_name = os.environ.get("POSTGRES_DB")

        if not all([db_user, db_password, db_host, db_name]):
            raise ValueError("Missing required database environment variables")

        logger.info(
            f"Database configuration: host={db_host}, user={db_user}, db={db_name}"
        )

        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
        logger.info(f"Attempting to connect to database at {db_host}")

        # Test connection with retries
        max_retries = 5
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                engine = create_engine(db_url)
                with engine.connect() as connection:
                    # Test connection with a simple query
                    connection.execute(text("SELECT 1"))
                    logger.info("Successfully connected to database")
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(
                        f"Failed to connect to database after {max_retries} attempts: {str(e)}"
                    )
                    raise
                logger.warning(
                    f"Connection attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)

        Session = sessionmaker(bind=engine)

        with engine.connect() as connection:
            logger.info("Creating schema and setting up user...")
            try:
                # Create schema and set up user
                connection.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
                logger.info("Schema created successfully")

            except Exception as e:
                logger.error(f"Error during schema/user setup: {str(e)}")
                raise

            # Create tables
            logger.info("Creating tables...")
            try:
                Base.metadata.create_all(engine, checkfirst=True)
                logger.info("Tables created/updated successfully")
            except Exception as e:
                logger.error(f"Error during table creation: {str(e)}")
                raise

            # Ensure all required columns exist in each table
            logger.info("Checking and adding required columns...")
            try:
                connection.execute(
                    text(
                        """
                    DO $$
                    BEGIN
                        -- Check and add columns to dishes table
                        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'dishes') THEN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'dishes' AND column_name = 'user_email') THEN
                                ALTER TABLE public.dishes ADD COLUMN user_email VARCHAR NOT NULL;
                            END IF;
                        END IF;

                        -- Check and add columns to dish_day table
                        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'dish_day') THEN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'dish_day' AND column_name = 'user_email') THEN
                                ALTER TABLE public.dish_day ADD COLUMN user_email VARCHAR NOT NULL;
                            END IF;
                        END IF;

                        -- Check and add columns to total_for_day table
                        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'total_for_day') THEN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'total_for_day' AND column_name = 'user_email') THEN
                                ALTER TABLE public.total_for_day ADD COLUMN user_email VARCHAR NOT NULL;
                            END IF;
                        END IF;

                        -- Check and add columns to weights table
                        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'weights') THEN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'weights' AND column_name = 'user_email') THEN
                                ALTER TABLE public.weights ADD COLUMN user_email VARCHAR NOT NULL;
                            END IF;
                        END IF;
                    END $$;
                """
                    )
                )
                logger.info("Column checks completed successfully")
            except Exception as e:
                logger.error(f"Error during column checks: {str(e)}")
                raise

            # Create indexes after ensuring columns exist
            logger.info("Creating indexes...")
            try:
                #     connection.execute(text("""
                #         DO $$
                #         BEGIN
                #             IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'dishes') THEN
                #                 CREATE INDEX IF NOT EXISTS idx_dishes_user_email ON public.dishes (user_email);
                #             END IF;

                #             IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'dish_day') THEN
                #                 CREATE INDEX IF NOT EXISTS idx_dish_day_user_email ON public.dish_day (user_email);
                #             END IF;

                #             IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'total_for_day') THEN
                #                 CREATE INDEX IF NOT EXISTS idx_total_for_day_user_email ON public.total_for_day (user_email);
                #             END IF;

                #             IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'weights') THEN
                #                 CREATE INDEX IF NOT EXISTS idx_weights_user_email ON public.weights (user_email);
                #             END IF;
                #         END $$;
                #     """))
                logger.info("Indexes created successfully")
            except Exception as e:
                logger.error(f"Error during index creation: {str(e)}")
                raise

    except Exception as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        raise


if __name__ == "__main__":
    create_tables()
