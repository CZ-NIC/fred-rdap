ARG PYTHON_VERSION=3.9
############################################################
# Base image
FROM python:${PYTHON_VERSION}-slim AS base
WORKDIR /app

RUN adduser --home /app --disabled-password --gecos 'rdap' rdap

############################################################
# Build image
FROM base AS build
ARG PIP_INDEX_URL=https://pypi.nic.cz/cznic/public

# Install build dependencies from debian
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and use virtualenv
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy source code
COPY . /app/src

# Install application and other dependencies
WORKDIR /app/src
RUN pip install --no-cache-dir \
        . \
        python-environ \
        sentry-sdk \
        # Install uwsgi for the python version in use.
        uwsgi


############################################################
# Uwsgi image
FROM base AS uwsgi

ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH="/app/uwsgi"
ENV DJANGO_SETTINGS_MODULE="rdap_settings"

# Install runtime dependencies
RUN apt-get --yes update \
    && apt-get install --yes --no-install-recommends \
        libxml2 \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtualenv
COPY --from=build /app/venv/ /app/venv/
# Copy the uwsgi configuration
COPY docker/uwsgi /app/uwsgi/

# Switch user
USER rdap:rdap

EXPOSE 16000

CMD ["uwsgi", "--ini", "/app/uwsgi/uwsgi.ini"]
