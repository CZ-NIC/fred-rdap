ARG PYTHON_VERSION=3.11
FROM reg.nic.cz/python/tox:${PYTHON_VERSION}
RUN apt-get --yes update \
# Install testing dependencies
 && apt-get install --yes --no-install-recommends \
    libomniorb4-2 \
 && rm -rf /var/lib/apt/lists/*
