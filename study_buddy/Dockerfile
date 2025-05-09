# --- Stage 1: Build environment ---
FROM python:3.11-slim-bookworm AS builder

WORKDIR /study_buddy

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libffi-dev python3-dev libssl-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application code and install dependencies
COPY study_buddy/ /study_buddy/
COPY study_buddy/requirements.txt .
RUN pip install --upgrade pip && pip install --user -r requirements.txt 


# --- Stage 2: Runtime environment ---
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /study_buddy

# Install only runtime system dependencies (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev libssl-dev supervisor curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"

RUN crewai install

# Copy application code and supervisor config
COPY study_buddy/ /study_buddy/
COPY supervisord.conf /etc/supervisord.conf

# Expose FastAPI port
EXPOSE 8000

# Start app and Celery via supervisor
CMD ["sh", "-c", "crewai install && supervisord -c /etc/supervisord.conf"]
