import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import (ARRAY, JSON, Column, Float, Integer, String,
                        create_engine, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_host = os.environ.get("POSTGRES_HOST")
db_name = os.environ.get("POSTGRES_DB")

DATABASE_URL = f"postgresql://postgres:{db_password}@{db_host}:5432/{db_name}"

engine = create_engine(DATABASE_URL)

Base = declarative_base()


def current_date():
    return datetime.now().date()


class DishesDay(Base):
    __tablename__ = "dishes_day"
    __table_args__ = {"schema": "public"}

    time = Column(Integer, primary_key=True)
    date = Column(String)
    dish_name = Column(String)
    estimated_avg_calories = Column(Integer)
    ingredients = Column(ARRAY(String))
    total_avg_weight = Column(Integer)
    contains = Column(JSON)
    user_email = Column(String, nullable=False)


class TotalForDay(Base):
    __tablename__ = "total_for_day"
    __table_args__ = {"schema": "public"}

    today = Column(String, primary_key=True)
    total_calories = Column(Integer)
    ingredients = Column(ARRAY(String))
    dishes_of_day = Column(ARRAY(String))
    total_avg_weight = Column(Integer)
    contains = Column(JSON)
    user_email = Column(String, nullable=False)


class Weight(Base):
    __tablename__ = "weight"
    __table_args__ = {"schema": "public"}

    time = Column(Integer, primary_key=True)
    date = Column(String)
    weight = Column(Float)
    user_email = Column(String, nullable=False)


Session = sessionmaker(bind=engine)


def write_to_dish_day(message=None, recalculate: Optional[bool] = False, user_email: str = None):
    try:
        session = Session()
        if not recalculate:
            dish_name = message.get("dish_name")
            estimated_avg_calories = message.get("estimated_avg_calories")
            ingredients = message.get("ingredients")
            total_avg_weight = message.get("total_avg_weight")
            contains = message.get("contains")

            # Insert the new dish entry
            dish_day = DishesDay(
                time=int(datetime.now().timestamp()),
                date=current_date(),
                dish_name=dish_name,
                estimated_avg_calories=estimated_avg_calories,
                ingredients=ingredients,
                total_avg_weight=total_avg_weight,
                contains=contains,
                user_email=user_email
            )

            session.add(dish_day)
            session.commit()

            logger.info(f"Successfully wrote dish data to database: {dish_name}")

        # Query aggregated data for the current date
        logger.info(f"Calculating total food data for {current_date()}")

        # Get total_calories, total_weight, all_dishes, all_contains
        total_data = (
            session.query(
                func.sum(DishesDay.estimated_avg_calories).label("total_calories"),
                func.sum(DishesDay.total_avg_weight).label("total_weight"),
                func.array_agg(DishesDay.dish_name).label("all_dishes"),
                func.json_agg(DishesDay.contains).label("all_contains"),
            )
            .filter(DishesDay.date == current_date())
            .filter(DishesDay.user_email == user_email)
            .one()
        )

        ingredients_subq = (
            session.query(func.unnest(DishesDay.ingredients).label("ingredient"))
            .filter(DishesDay.date == current_date())
            .filter(DishesDay.user_email == user_email)
            .subquery()
        )

        all_ingredients_result = session.query(
            func.array_agg(ingredients_subq.c.ingredient).label("all_ingredients")
        ).one()

        all_ingredients = all_ingredients_result.all_ingredients or []

        total_calories = total_data.total_calories or 0
        total_weight = total_data.total_weight or 0
        all_dishes = (
            [dish for dish in total_data.all_dishes if dish]
            if total_data.all_dishes
            else []
        )

        all_contains = total_data.all_contains or []
        aggregated_contains = {"proteins": 0, "fats": 0, "carbohydrates": 0, "sugar": 0}
        for entry in all_contains:
            for key in aggregated_contains:
                aggregated_contains[key] += entry.get(key, 0)

        # Prepare data for total_for_day table
        total_for_day = TotalForDay(
            today=current_date(),
            total_calories=total_calories,
            ingredients=all_ingredients,
            dishes_of_day=all_dishes,
            total_avg_weight=total_weight,
            contains=aggregated_contains,
            user_email=user_email
        )

        # Check if there's an existing entry for today
        existing_entry = (
            session.query(TotalForDay)
            .filter(TotalForDay.today == current_date())
            .filter(TotalForDay.user_email == user_email)
            .first()
        )
        if existing_entry:
            logger.info("Updating existing entry in total_for_day table")
            existing_entry.total_calories = total_calories
            existing_entry.ingredients = all_ingredients
            existing_entry.dishes_of_day = all_dishes
            existing_entry.total_avg_weight = total_weight
            existing_entry.contains = aggregated_contains
        else:
            logger.info("Inserting new entry in total_for_day table")
            session.add(total_for_day)

        session.commit()

        logger.info(
            f"Successfully wrote aggregated data to total_for_day for {current_date()}"
        )

    except Exception as e:
        logger.error(f"Error writing to database: {e}")

    finally:
        session.close()


def get_today_dishes(user_email: str = None):
    try:
        session = Session()
        latest_weight_entry = (
            session.query(Weight)
            .filter(Weight.user_email == user_email)
            .order_by(Weight.time.desc())
            .first()
        )

        total_data = (
            session.query(TotalForDay)
            .filter(TotalForDay.today == current_date())
            .filter(TotalForDay.user_email == user_email)
            .first()
        )
        if not total_data:
            logger.info(f"No data found in total_for_day for {current_date()}")
            total_for_day_data = {
                "total_calories": 0,
                "total_avg_weight": latest_weight_entry.weight
                if latest_weight_entry
                else 0,
                "contains": [],
            }
            dishes_list = []
            result = {
                "total_for_day": total_for_day_data,
                "dishes_today": dishes_list,
            }
            if latest_weight_entry:
                result["latest_weight"] = {
                    "time": latest_weight_entry.time,
                    "weight": latest_weight_entry.weight,
                }
            return result
        total_for_day_data = {
            "total_calories": total_data.total_calories,
            "total_avg_weight": total_data.total_avg_weight,
            "contains": total_data.contains,
        }
        dishes_today = (
            session.query(DishesDay)
            .filter(DishesDay.date == current_date())
            .filter(DishesDay.user_email == user_email)
            .all()
        )
        dishes_list = [
            {
                "time": dish.time,
                "dish_name": dish.dish_name,
                "estimated_avg_calories": dish.estimated_avg_calories,
                "total_avg_weight": dish.total_avg_weight,
                "ingredients": dish.ingredients,
            }
            for dish in dishes_today
        ]
        result = {
            "total_for_day": total_for_day_data,
            "dishes_today": dishes_list,
        }
        if latest_weight_entry:
            result["latest_weight"] = {
                "time": latest_weight_entry.time,
                "weight": latest_weight_entry.weight,
            }

        logger.info(f"Result of get_today_dishes {result}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving today's dishes: {e}")
        return {}


def delete_food(time, user_email: str = None):
    logger.info(f"Deleting food with time {time} from db")
    try:
        session = Session()
        # Handle case where time is passed as a dictionary with time and user_email
        if isinstance(time, dict) and 'time' in time:
            time_value = time['time']
            user_email = time.get('user_email', user_email)
        else:
            time_value = time
        
        rows_deleted = (
            session.query(DishesDay)
            .filter(DishesDay.time == time_value)
            .filter(DishesDay.user_email == user_email)
            .delete()
        )
        session.commit()
        if rows_deleted > 0:
            logger.info(
                f"Successfully deleted {rows_deleted} food entries with time {time_value} from database"
            )
            write_to_dish_day(recalculate=True, user_email=user_email)
        else:
            logger.info(f"No food entries found with time {time_value}")
    except Exception as e:
        logger.error(f"Error deleting food from database: {e}")
    finally:
        session.close()


def write_weight(weight, user_email: str = None):
    try:
        session = Session()
        weight_entry = Weight(
            time=int(datetime.now().timestamp()),
            date=current_date(),
            weight=weight,
            user_email=user_email
        )
        session.add(weight_entry)
        session.commit()
        logger.info(f"Successfully wrote weight data to database: {weight}")
    except Exception as e:
        logger.error(f"Error writing weight to database: {e}")
    finally:
        session.close()


def get_dishes(days, user_email: str = None):
    try:
        logger.info(f"Starting get_dishes function with days={days}")
        session = Session()
        logger.info("Database session created successfully.")
        today = datetime.now()
        start_date = today - timedelta(days=days)
        dishes = (
            session.query(DishesDay)
            .filter(DishesDay.date.between(start_date, today))
            .filter(DishesDay.user_email == user_email)
            .all()
        )

        dishes_list = [
            {
                "time": dish.time,
                "date": dish.date,
                "dish_name": dish.dish_name,
                "estimated_avg_calories": dish.estimated_avg_calories,
                "total_avg_weight": dish.total_avg_weight,
                "ingredients": dish.ingredients,
                "contains": dish.contains,
            }
            for dish in dishes
        ]
        return dishes_list
    except Exception as e:
        logger.error(f"Error retrieving dishes from database: {e}", exc_info=True)
        return []
    finally:
        session.close()
