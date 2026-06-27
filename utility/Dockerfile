FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    python -m pip install --prefer-binary -r requirements.txt

COPY . .

RUN chmod +x /app/utility/bin/entrypoint.sh && \
    mkdir -p /app/logs /app/storage/static /app/storage/static_collected /app/storage/media && \
    chown -R app:app /app

USER app

ENTRYPOINT ["/app/utility/bin/entrypoint.sh"]
