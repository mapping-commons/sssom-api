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
ENV JAVA_OPTS=-Xmx10G
RUN wget -nv https://github.com/blazegraph/database/releases/download/BLAZEGRAPH_2_1_6_RC/blazegraph.jar

# java -server -Xmx10G -Dcom.bigdata.rdf.sail.webapp.ConfigParams.propertyFile=/RWStore.properties -jar blazegraph.jar
CMD ["java", "-server", "-Xmx10G", "-Dcom.bigdata.rdf.sail.webapp.ConfigParams.propertyFile=/RWStore.properties", "-Dcom.bigdata.util.config.LogUtil=/log4.properties", "-jar", "blazegraph.jar"]
###### blazegraph-runner #####
#ENV BR=1.7
#ENV PATH "/tools/blazegraph-runner/bin:$PATH"
#RUN wget -nv https://github.com/balhoff/blazegraph-runner/releases/download/v$BR/blazegraph-runner-$BR.tgz \
#&& tar -zxvf blazegraph-runner-$BR.tgz \
#&& mv blazegraph-runner-$BR /tools/blazegraph-runner

