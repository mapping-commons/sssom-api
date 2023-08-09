FROM anitacaron/blazegraph:v0.3.1

VOLUME /data

ENV WORKSPACE=/opt/SSSOM
WORKDIR /opt/SSSOM

# ENV BUILD_OUTPUT=${WORKSPACE}/build.out
COPY /data/ols /data
COPY /data/dataloader.xml /opt/SSSOM/dataloader.xml
COPY process.sh /opt/SSSOM/process.sh
# COPY rdf4j_sssom.txt /opt/SSSOM/rdf4j_sssom.txt

RUN chmod +x /opt/SSSOM/*.sh

CMD ["/opt/SSSOM/process.sh"]