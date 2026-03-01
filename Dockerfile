
# STAGE 1: BUILDER
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment inside the container
RUN python -m venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy ONLY the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt


# ==========================================
# STAGE 2: THE RUNNER (PRODUCTION)
# ==========================================
# We start fresh from a brand new, clean image
FROM python:3.12-slim

# Set environment variables for the runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# THE MAGIC TRICK: 
# Copy the pre-built virtual environment from the 'builder' stage.
# This leaves all the heavy compilers (gcc, build-essential) behind!
COPY --from=builder /opt/venv /opt/venv

# Copy your actual FastAPI application code
# (Assuming your code is in the src/ folder)
COPY . .

# RUN python train.py

# Expose the port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]