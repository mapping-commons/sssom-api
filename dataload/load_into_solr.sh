#!/usr/bin/env bash

if [ $# == 0 ]; then
    echo "Usage: $0 <solrpath> <jsonlpath>"
    exit 1
fi

$1/bin/solr start -force -Djetty.host=127.0.0.1
sleep 10


echo Uploading mappings from $2 to solr
ls -hl $2

wget --method POST --no-proxy -O - --server-response --content-on-error=on --header="Content-Type: application/json" --body-file $2 \
    http://127.0.0.1:8983/solr/sssom_mappings/update/json/docs?commit=true
sleep 5



echo Uploading mapping sets from $3 to solr
ls -hl $3

wget --method POST --no-proxy -O - --server-response --content-on-error=on --header="Content-Type: application/json" --body-file $3 \
    http://127.0.0.1:8983/solr/sssom_mapping_sets/update/json/docs?commit=true
sleep 5


echo Uploading stats from $4 to solr
ls -hl $4

wget --method POST --no-proxy -O - --server-response --content-on-error=on --header="Content-Type: application/json" --body-file $4 \
    http://127.0.0.1:8983/solr/sssom_stats/update/json/docs?commit=true
sleep 5


wget http://localhost:8983/solr/sssom_mapping_sets/update?commit=true
sleep 5

wget http://localhost:8983/solr/sssom_mappings/update?commit=true
sleep 5

wget http://localhost:8983/solr/sssom_stats/update?commit=true
sleep 5




$1/bin/solr stop



