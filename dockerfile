FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY netwatch ./netwatch

EXPOSE 8000

CMD ["uvicorn", "netwatch.api:app", "--host", "0.0.0.0", "--port", "8000"]
