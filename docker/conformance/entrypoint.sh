#!/bin/sh
set -e

# Start fake RDAP backend.
/app/venv/bin/python /app/docker/conformance/mock_grpc.py &

if [ "$1" = "" ]; then
    uwsgi --ini /app/docker/conformance/uwsgi.ini
else
    exec "$@"
fi
