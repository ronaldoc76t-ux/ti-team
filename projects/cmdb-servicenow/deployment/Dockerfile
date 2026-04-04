FROM python:3.11-slim

# Labels
LABEL maintainer="TI Team"
LABEL description="CMDB ServiceNow Discovery"

# Arguments
ARG BUILD_DATE
ARG VCS_REF

# Build labels
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.vcs-ref=$VCS_REF
LABEL org.label-schema.name="cmdb-discovery"
LABEL org.label-schema.description="CMDB ServiceNow Discovery"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CONFIG_PATH=/app/config/config.yaml

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libsnmp-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY implementation/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy application
COPY implementation/ /app/
COPY config/ /app/config/
COPY scripts/ /app/scripts/

# Create log directory
RUN mkdir -p /var/log && chown -R nobody:nogroup /var/log

# Set execute permissions on scripts
RUN chmod +x /app/scripts/*.sh

# Switch to non-root user
USER nobody

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD /app/scripts/health-check.sh || exit 1

# Default command
CMD ["/app/scripts/run-discovery.sh"]