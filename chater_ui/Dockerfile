FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    vim \
    curl \
    && apt-get clean
RUN useradd -m app
USER app

WORKDIR /app

# Add user's local bin to PATH for pip-installed executables
ENV PATH="/home/app/.local/bin:$PATH"

COPY requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV PYTHONPATH=/app

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app.app:app"]
