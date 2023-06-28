import csv
import argparse
import os
from pathlib import Path
from collections import defaultdict
from sssom.parsers import parse_sssom_table

from sssom_stream import get_sssom_tsv_headers
from sssom_stream import stream_sssom_tsv

from ordered_set import OrderedSet

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="sssom tsv file or directory containing tsv files")
    parser.add_argument("--output", required=True,
                        help="path for output solr jsonl file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_dir():
        input_files = [f for f in input_path.iterdir(
        ) if f.is_file() and f.suffix == ".tsv"]
    else:
        input_files = [input_path]

    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        for file in input_files:
            write_mappings(file, output_file)

def write_mappings(input_file, nodes_writer, edges_writer, printed_node_ids, node_ids_to_print, edge_headers):

    mapping_set = stream_sssom_tsv(input_file)
    mapping_set_header = next(mapping_set)

    # Iterate over the TSV lines
    for line in mapping_set:
        subj_id = line["subject_id"]
        subj_label = line["subject_label"]
        obj_id = line["object_id"]
        obj_label = line["object_label"]

        add_node(subj_id, subj_label, input_file, nodes_writer,
                 edges_writer, printed_node_ids, node_ids_to_print, edge_headers)
        add_node(obj_id, obj_label, input_file, nodes_writer,
                 edges_writer, printed_node_ids, node_ids_to_print, edge_headers)

        row = [None] * len(edge_headers)
        for col, header in enumerate(edge_headers):
            if header == ":START_ID":
                row[col] = subj_id
            elif header == ":TYPE":
                row[col] = line["predicate_id"]
            elif header == ":END_ID":
                row[col] = obj_id
            else:
                row[col] = line[header]
        edges_writer.writerow(row)

def add_node(node_id, node_label, input_file, nodes_writer, edges_writer, printed_node_ids,
             node_ids_to_print, edge_headers):
    if node_id in printed_node_ids or node_id in node_ids_to_print:
        return

    if not node_label:
        node_ids_to_print.add(node_id)
        return

    node_ids_to_print.discard(node_id)
    printed_node_ids.add(node_id)

    print_node(node_id, node_label, nodes_writer)


def print_node(node_id, node_label, nodes_writer):
    curie_prefix = node_id.split(":")[0]
    curie_local_part = node_id.split(":")[1]

    nodes_writer.writerow(
        [node_id, "MappedEntity", node_label, curie_prefix, curie_local_part])


if __name__ == "__main__":
    main()
