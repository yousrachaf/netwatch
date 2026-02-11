FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY netwatch /app/netwatch
COPY tests /app/tests

RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir -e . \
 && pip install --no-cache-dir pytest

EXPOSE 8000

CMD ["uvicorn", "netwatch.api:app", "--host", "0.0.0.0", "--port", "8000"]
