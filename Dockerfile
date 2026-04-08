FROM python:3.12-slim

WORKDIR /opt/loltopnews

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY data/ ./data/

EXPOSE 8000

WORKDIR /opt/loltopnews/app
CMD sh -c "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"
