import logging
import os
from sqlalchemy import create_engine, Column, Integer, String, Date, ARRAY, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()


class DishesDay(Base):
    __tablename__ = 'dishes_day'
    __table_args__ = {'schema': 'public'}

    time = Column(Integer, primary_key=True)
    date = Column(String)
    dish_name = Column(String)
    estimated_avg_calories = Column(Integer)
    ingredients = Column(ARRAY(String))
    total_avg_weight = Column(Integer)
    contains = Column(JSON)


class TotalForDay(Base):
    __tablename__ = 'total_for_day'
    __table_args__ = {'schema': 'public'}

    today = Column(String, primary_key=True)
    total_calories = Column(Integer)
    ingredients = Column(ARRAY(String))
    dishes_of_day = Column(ARRAY(String))
    total_avg_weight = Column(Integer)
    contains = Column(JSON)


def create_tables():
    try:
        db_user = os.environ.get('POSTGRES_USER')
        db_password = os.environ.get('POSTGRES_PASSWORD')
        db_host = os.environ.get('POSTGRES_HOST')
        db_name = os.environ.get('POSTGRES_DB')

        db_url = f'postgresql://postgres:{db_password}@{db_host}:5432/{db_name}'

        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)

        with engine.connect() as connection:
            connection.execute(text(f"ALTER USER {db_user} WITH PASSWORD '{db_password}'"))
            logger.info(text(f"ALTER USER {db_user} WITH PASSWORD '{db_password}'"))

            connection.execute(text("CREATE SCHEMA IF NOT EXISTS public"))

            Base.metadata.create_all(engine, checkfirst=True)
            logger.info("Tables created/updated successfully")

            for table in Base.metadata.tables.keys():
                connection.execute(text(f"ALTER TABLE {table} OWNER TO {db_user}"))
                logger.info(f"Ownership of table '{table}' granted to user '{db_user}'")

    except Exception as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")


if __name__ == "__main__":
    create_tables()