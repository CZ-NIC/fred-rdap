ARG PYTHON_VERSION=3.9
FROM archive.nic.cz:5000/python/tox:${PYTHON_VERSION}
RUN apt-get --yes update \
 && apt-get install --yes --no-install-recommends \
    curl \
    # Dependencies of the RDAP & RDAP backend mock.
    libomniorb4-2 \
    omniorb-nameserver \
 && rm -rf /var/lib/apt/lists/*

# Prepare rdap
WORKDIR /app
COPY . .
ENV PIP_INDEX_URL=https://pypi.nic.cz/cznic/public
RUN tox --devenv venv

ENV PYTHONPATH="/app/docker/conformance:$PYTHONPATH"
ENV DJANGO_SETTINGS_MODULE="settings"

EXPOSE 8000
ENTRYPOINT ["/app/docker/conformance/entrypoint.sh"]
CMD [""]
