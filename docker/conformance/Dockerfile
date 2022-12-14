ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# Install build dependencies from debian
RUN apt-get update \
 && apt-get install --yes --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

ARG PIP_INDEX_URL=https://pypi.nic.cz/cznic/public
WORKDIR /app
COPY . .

# Create and use virtualenv
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install application and dependencies
RUN pip install --no-cache-dir \
        . \
        # Install uwsgi for the python version in use.
        uwsgi

ENV PYTHONPATH="/app/docker/conformance:$PYTHONPATH"
ENV DJANGO_SETTINGS_MODULE="settings"

EXPOSE 8000
ENTRYPOINT ["/app/docker/conformance/entrypoint.sh"]
CMD [""]
