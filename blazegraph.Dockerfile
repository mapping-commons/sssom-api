FROM ubuntu:20.04
WORKDIR /tools

# Install base tools from Ubuntu.
RUN apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
        wget \
        curl \
        openjdk-11-jdk \
        ca-certificates \
        ca-certificates-java

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

###### Blazegraph #####
ENV JAVA_OPTS -Xmx16G
RUN wget -nv https://github.com/blazegraph/database/releases/download/BLAZEGRAPH_2_1_6_RC/blazegraph.jar

CMD java -server $JAVA_OPTS -Dcom.bigdata.rdf.sail.webapp.ConfigParams.propertyFile=/RWStore.properties -Dcom.bigdata.util.config.LogUtil=/log4.properties -jar blazegraph.jar


