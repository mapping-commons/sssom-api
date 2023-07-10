#!/usr/bin/env bash

if [ $# == 0 ]; then
    echo "Usage: $0 <indir> <outdir>"
    exit 1
fi

SCRIPT_PATH=$(dirname $(readlink -f $0))

INDIR=$1
OUTDIR=$2

rm -f $OUTDIR/*

echo sssom2neo
python3 $SCRIPT_PATH/src/sssom2neo.py --input $INDIR --output-nodes $OUTDIR/nodes.csv --output-edges $OUTDIR/edges.csv

echo sssom2solr
python3 $SCRIPT_PATH/src/sssom2solr.py --input $INDIR --output $OUTDIR/nodes.jsonl

