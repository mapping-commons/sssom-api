FROM ubuntu:20.04
WORKDIR /tools

# Install base tools from Ubuntu.
RUN apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
        unzip \
        git \
        wget

###### blazegraph-runner #####
ENV BR=1.7
ENV PATH "/tools/blazegraph-runner/bin:$PATH"
RUN wget -nv https://github.com/balhoff/blazegraph-runner/releases/download/v$BR/blazegraph-runner-$BR.tgz \
&& tar -zxvf blazegraph-runner-$BR.tgz \
&& mv blazegraph-runner-$BR /tools/blazegraph-runner

