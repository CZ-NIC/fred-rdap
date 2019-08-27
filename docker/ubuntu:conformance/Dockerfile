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
# Requirements for the conformance test
RUN apt-get --yes update \
 && apt-get install --yes --no-install-recommends \
    git \
    libomniorb4-2 \
    maven \
    omniidl-python \
    omniorb-nameserver \
    openjdk-8-jdk \
    python \
    python-omniorb \
    python-setuptools \
    ssh \
 && rm -rf /var/lib/apt/lists/*
# Install newest pip
RUN apt-get --yes update \
 && apt-get install --yes --no-install-recommends \
    python-pip \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --upgrade \
    pip \
 && apt-get purge --yes python-pip
