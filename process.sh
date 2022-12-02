#!/bin/bash

set -e

echo "process started"
echo "Start: upload-triplestore"
echo "TIME:"
date

SETUP=${WORKSPACE}/rdf4j_sssom.txt
RDF4J=/opt/eclipse-rdf4j-${RDF4J_VERSION}
RDF4JSERVER=${SERVER}/rdf4j-server
DATA=/data

if [ `ls $DATA/*.jsonld.gz | wc -l` -lt 1 ]; then echo "ERROR: No data in data directory! Aborting.. " && exit 1; fi

echo 'Waiting for RDF4J server..'
until $(curl --output /dev/null --silent --head --fail ${RDF4JSERVER}); do
    printf '.'
    sleep 5
done

echo "connect "${RDF4JSERVER}|cat - ${SETUP} > /tmp/out && mv /tmp/out ${SETUP}
cat ${SETUP}
cat ${SETUP} | sh ${RDF4J}/bin/console.sh

ls -lh $DATA


echo "TIME:"
date

cd $DATA

# The following for loop writes the load commands into the RDF4J setup script
for i in *.jsonld.gz; do
    [ -f "$i" ] || break
    #arg="load "$DATA/$i" into ns:"$i
    echo $i
    #awk -v line="$arg" '/open vfb/ { print; print line; next }1' $WS/rdf4j.txt > $WS/tmp.txt
    #cp $WS/tmp.txt $WS/rdf4j.txt
    # URI="%3Chttp%3A%2F%2Fvirtualflybrain.org%2Fdata%2FVFB%2FOWL%2F${i}%3E"
    echo "curl -v --retry 5 --retry-delay 10 -X POST -H \"Content-type: application/ld+json\" --data-binary @$i ${RDF4JSERVER}/repositories/sssom/statements?context=null"
    curl -v --retry 5 --retry-delay 10 -X POST -H "Content-type: application/ld+json" --data-binary @$i ${RDF4JSERVER}/repositories/sssom/statements?context=null || exit 1
    echo "TIME:"
    date
    sleep 5
done


echo "End: upload-triplestore"
echo "TIME:"
date
echo "process complete"