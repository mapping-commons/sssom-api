#!/usr/bin/env bash

if [ $# == 0 ]; then
    echo "Usage: $0 <solrpath> <jsonlpath>"
    exit 1
fi

$1/bin/solr start -force -Djetty.host=127.0.0.1
sleep 10

wget --method POST --no-proxy -O - --server-response --content-on-error=on --header="Content-Type: application/json" --body-file $2 \
    http://127.0.0.1:8983/solr/oxo2_nodes/update/json/docs?commit=true

sleep 5

wget http://localhost:8983/solr/ols4_entities/update?commit=true

sleep 5

wget http://localhost:8983/solr/ols4_autocomplete/update?commit=true

sleep 5

$1/bin/solr stop



