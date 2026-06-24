# syntax=docker/dockerfile:1
# Render Web Service — Python API + React static (monorepo)
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# Python deps (Playwright browsers có sẵn trong image)
COPY MAIN_AUTOMATION_TEST/requirements-server.txt ./MAIN_AUTOMATION_TEST/
RUN pip install --no-cache-dir -r MAIN_AUTOMATION_TEST/requirements-server.txt

# Build React dashboard (public mode — khóa sidebar admin)
COPY MAIN_AUTOMATION_TEST_FE/package.json MAIN_AUTOMATION_TEST_FE/package-lock.json ./MAIN_AUTOMATION_TEST_FE/
RUN cd MAIN_AUTOMATION_TEST_FE && npm ci
COPY MAIN_AUTOMATION_TEST_FE/ ./MAIN_AUTOMATION_TEST_FE/
RUN cd MAIN_AUTOMATION_TEST_FE && npm run build:web

# Backend source + test data
COPY MAIN_AUTOMATION_TEST/ ./MAIN_AUTOMATION_TEST/

WORKDIR /app/MAIN_AUTOMATION_TEST

ENV RESTRICT_ADMIN=1
ENV API_HOST=0.0.0.0
ENV HEADLESS=1
ENV PYTHONUNBUFFERED=1

EXPOSE 10000
CMD ["python", "-m", "api"]
