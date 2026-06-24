# syntax=docker/dockerfile:1
# Stage 1 — Build React (Node image có npm)
FROM node:20-bookworm-slim AS fe-builder
WORKDIR /fe
COPY MAIN_AUTOMATION_TEST_FE/package.json MAIN_AUTOMATION_TEST_FE/package-lock.json ./
RUN npm ci
COPY MAIN_AUTOMATION_TEST_FE/ ./
RUN npm run build:web

# Stage 2 — Python API + Playwright (không cần Node runtime)
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

COPY MAIN_AUTOMATION_TEST/requirements-server.txt ./MAIN_AUTOMATION_TEST/
RUN pip install --no-cache-dir -r MAIN_AUTOMATION_TEST/requirements-server.txt

COPY MAIN_AUTOMATION_TEST/ ./MAIN_AUTOMATION_TEST/
COPY --from=fe-builder /fe/dist ./MAIN_AUTOMATION_TEST_FE/dist

WORKDIR /app/MAIN_AUTOMATION_TEST

ENV RESTRICT_ADMIN=1
ENV API_HOST=0.0.0.0
ENV HEADLESS=1
ENV PYTHONUNBUFFERED=1

EXPOSE 10000
CMD ["python", "-m", "api"]
