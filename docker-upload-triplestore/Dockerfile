FROM eclipse/rdf4j-workbench

VOLUME /data

ENV WORKSPACE=/opt/SSSOM

ENV BUILD_OUTPUT=${WORKSPACE}/build.out

COPY docker-upload-triplestore/process.sh /opt/SSSOM/process.sh
COPY docker-upload-triplestore/rdf4j_sssom.txt /opt/SSSOM/rdf4j_sssom.txt

RUN chmod +x /opt/SSSOM/*.sh

CMD ["/opt/SSSOM/process.sh"]