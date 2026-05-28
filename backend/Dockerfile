# Use the official Playwright Python image which includes all Chromium dependencies
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install uv for fast package installation
RUN pip install uv

# Copy requirements and install dependencies globally in the container
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# The base image already has browsers, but we ensure the specific chromium is ready
RUN playwright install chromium

# Create necessary directories
RUN mkdir -p /app/app/core /app/app/models /app/app/api /app/app/services

# Copy the application code
COPY . .

# Ensure Python output is not buffered
ENV PYTHONUNBUFFERED=1

# The command will be overridden by docker-compose for api/scheduler
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
