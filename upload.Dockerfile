FROM anitacaron/blazegraph:v0.4

VOLUME /data

ENV WORKSPACE=/opt/SSSOM
WORKDIR /opt/SSSOM


COPY /config/dataloader.xml /opt/SSSOM/dataloader.xml
COPY process.sh /opt/SSSOM/process.sh

RUN chmod +x /opt/SSSOM/*.sh

CMD ["/opt/SSSOM/process.sh"]