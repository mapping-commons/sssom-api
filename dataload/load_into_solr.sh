#!/usr/bin/env bash

if [ $# == 0 ]; then
    echo "Usage: $0 <solrpath> <jsonlpath>"
    exit 1
fi

$1/bin/solr start -force -Djetty.host=127.0.0.1
sleep 10

echo Uploading file $2 to solr
ls -hl $2

wget --method POST --no-proxy -O - --server-response --content-on-error=on --header="Content-Type: application/json" --body-file $2 \
    http://127.0.0.1:8983/solr/sssom_mappings/update/json/docs?commit=true
sleep 5

wget http://localhost:8983/solr/sssom_mappings/update?commit=true
sleep 5

$1/bin/solr stop



