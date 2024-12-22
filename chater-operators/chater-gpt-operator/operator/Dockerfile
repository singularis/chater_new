FROM python:3.13-slim

RUN pip install kopf kubernetes

COPY operator.py /operator.py

CMD ["kopf", "run", "/operator.py", "--verbose"]
