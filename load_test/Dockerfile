FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    vim \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m app
USER app

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8089

ENV PYTHONUNBUFFERED=1
ENV PATH="/home/app/.local/bin:${PATH}"

CMD ["python", "-m", "locust", "-f", "/app/locustfile.py", "--web-host", "0.0.0.0"]