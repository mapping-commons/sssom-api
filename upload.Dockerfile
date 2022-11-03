FROM yyz1989/rdf4j:latest

VOLUME /data

ENV WORKSPACE=/opt/SSSOM
WORKDIR /opt/SSSOM

ENV BUILD_OUTPUT=${WORKSPACE}/build.out

COPY process.sh /opt/SSSOM/process.sh
COPY rdf4j_sssom.txt /opt/SSSOM/rdf4j_sssom.txt

RUN chmod +x /opt/SSSOM/*.sh

CMD ["/opt/SSSOM/process.sh"]