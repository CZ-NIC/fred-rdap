FROM ubuntu:xenial
# Requirements for the APT key
RUN apt-get --yes update \
 && apt-get install --yes --no-install-recommends \
    ca-certificates \
    gnupg \
    wget \
 && rm -rf /var/lib/apt/lists/*
RUN printf 'deb http://archive.nic.cz/ubuntu xenial main\n' > /etc/apt/sources.list.d/cz.nic.list
RUN wget --quiet --output-document=- https://archive.nic.cz/ubuntu/dists/cznic-archive-keyring.gpg | apt-key add -
# Requirements for the python test environment
RUN apt-get --yes update \
 && apt-get install --yes --no-install-recommends \
    git \
    libomniorb4-2 \
    omniidl-python \
    python3-dev \
    python3-setuptools \
    ssh \
 && rm -rf /var/lib/apt/lists/*
# CA CZ.NIC
RUN wget -O /etc/ssl/certs/cz.nic2-cacert.pem https://archive.nic.cz/private/cz.nic2-cacert.pem \
 && update-ca-certificates
# Install newest pip, tox and its plugins
RUN apt-get --yes update \
 && apt-get install --yes --no-install-recommends \
    python3-pip \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --upgrade \
    pip \
    tox \
    git+https://gitlab.office.nic.cz/tomas.pazderka/tox-version-plugin.git \
    tox-DEBIAN \
 && apt-get purge --yes python3-pip
# Update apt cache for tox debian plugin
RUN apt-get update
