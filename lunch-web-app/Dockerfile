# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY lunch-web-app/frontend/package*.json ./
RUN npm ci
COPY lunch-web-app/frontend/ ./
RUN npm run build

# Stage 2: Python backend + static assets
FROM python:3.12-slim
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

# Install Python dependencies
COPY pyproject.toml ./pyproject.toml
COPY lunch-web-app/requirements.txt ./requirements-webapp.txt
RUN uv pip install --system --no-cache . -r requirements-webapp.txt

# Copy web app backend
COPY lunch-web-app/backend/ ./lunch-web-app/backend/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./lunch-web-app/frontend/dist

EXPOSE 8000

WORKDIR /app/lunch-web-app
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "120"]
