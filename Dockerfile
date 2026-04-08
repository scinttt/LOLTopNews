# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim
WORKDIR /opt/loltopnews

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY --from=frontend-build /build/dist ./frontend/dist

RUN mkdir -p data/cache

EXPOSE 8000

WORKDIR /opt/loltopnews/app
CMD sh -c "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"
