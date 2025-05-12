# --- Stage 1: Build environment ---
FROM python:3.11-slim-bookworm AS builder

WORKDIR /study_buddy

# Install only essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libffi-dev python3-dev libssl-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker layer caching
COPY study_buddy/requirements.txt .

# Install Python dependencies in a virtual environment to isolate them
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

# --- Stage 2: Runtime environment ---
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /study_buddy

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev libssl-dev supervisor curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the virtual environment as the default Python environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code and supervisor config
COPY study_buddy/ /study_buddy/
COPY supervisord.conf /etc/supervisord.conf

# Expose FastAPI port
EXPOSE 8000

# Create a non-root user and set permissions
RUN useradd -m appuser && chown -R appuser:appuser /study_buddy

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown appuser:appuser /entrypoint.sh

# Switch to the non-root user
USER appuser

# Start the application
CMD ["/entrypoint.sh"]