# Use a minimal Python base image
FROM python:3.11-slim-bookworm

# Set the working directory
WORKDIR /study_buddy

# Copy application code into the container
COPY study_buddy/ /study_buddy/

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libffi-dev python3-dev libssl-dev supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip and dependencies from pyproject.toml using CrewAI
# Copy pyproject.toml and ensure CrewAI installs dependencies correctly
RUN pip install -r requirements.txt && crewai install

# Expose the application port for FastAPI
EXPOSE 8000

# Copy Supervisor configuration
COPY supervisord.conf /etc/supervisord.conf

# Command to start Supervisor, which will manage FastAPI and Celery worker
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
