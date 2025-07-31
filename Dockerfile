FROM python:3.11.9-alpine3.19

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies & shared libraries
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    openssl-dev \
    python3-dev \
    build-base \
    libpq \
    && rm -rf /var/cache/apk/*

# Install Python dependencies
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Expose Flask port
EXPOSE 3141

# Run via Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3141", "--workers", "4", "main:app"]
