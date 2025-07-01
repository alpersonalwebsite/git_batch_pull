# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_PATH="/opt/poetry/bin/poetry" \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/opt/poetry/cache

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy dependency files
WORKDIR /app
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --only=main --no-dev --no-interaction --no-ansi

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r gituser && useradd -r -g gituser gituser

# Set up working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=gituser:gituser src/ ./src/
COPY --chown=gituser:gituser pyproject.toml ./
COPY --chown=gituser:gituser README.md LICENSE ./

# Install the application
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install -e .

# Create directory for SSH keys and Git config
RUN mkdir -p /home/gituser/.ssh && \
    mkdir -p /home/gituser/.config/git && \
    chown -R gituser:gituser /home/gituser

# Switch to non-root user
USER gituser

# Set environment variables
ENV PYTHONPATH="/app/src:$PYTHONPATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD git-batch-pull --help || exit 1

# Default entrypoint
ENTRYPOINT ["git-batch-pull"]
CMD ["--help"]

# Metadata
LABEL maintainer="Al Diaz <aldiazcode@gmail.com>" \
      description="Git Batch Pull - Enterprise GitHub repository batch processing tool" \
      version="1.0.0" \
      org.opencontainers.image.source="https://github.com/yourusername/git-batch-pull" \
      org.opencontainers.image.documentation="https://github.com/yourusername/git-batch-pull/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT"
