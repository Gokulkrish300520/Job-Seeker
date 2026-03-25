# Multi-stage Dockerfile for Job Fetcher application
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy pip packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY config.py .
COPY main.py .
COPY scheduler.py .
COPY requirements.txt .

# Set environment to production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default entry point: run scheduler (production mode)
# To run in development mode, override with: python main.py
CMD ["python", "scheduler.py"]
