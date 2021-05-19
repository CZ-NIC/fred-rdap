#!/bin/sh
set -e

# Start fake RDAP backend.
omniNames -start &
/app/venv/bin/python /app/docker/conformance/mock_fred.py &

if [ "$1" = "" ]; then
    # This is defined here, because `hostname` command can't be used in Dockerfile CMD directive.
    /app/venv/bin/django-admin runserver "$(hostname):8000"
else
    exec "$@"
fi
