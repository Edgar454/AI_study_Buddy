# --- Stage 1: Builder ---
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libffi-dev python3-dev libssl-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY study_buddy /app

RUN pip install --upgrade pip && pip install uv && pip install crewai
RUN crewai install

# --- Stage 2: Runtime ---
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev libssl-dev supervisor curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app
COPY --from=builder /app/.venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV TMPDIR=/app/tmp

COPY supervisord.conf /etc/supervisord.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /app/tmp /app/logs

EXPOSE 8000
CMD ["/entrypoint.sh"]
