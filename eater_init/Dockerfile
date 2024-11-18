FROM python:3.12-slim

RUN pip install psycopg2-binary sqlalchemy

COPY create_tables.py /

ENTRYPOINT ["python3", "/create_tables.py"]