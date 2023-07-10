import csv
import argparse
import os
from pathlib import Path
from collections import defaultdict
from sssom.parsers import parse_sssom_table

from sssom_stream import get_sssom_tsv_headers

from ordered_set import OrderedSet

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="sssom tsv file or directory containing tsv files")
    parser.add_argument("--output-nodes", required=True,
                        help="path for output nodes tsv file")
    parser.add_argument("--output-edges", required=True,
                        help="path for output edges tsv file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_nodes_path = Path(args.output_nodes)
    output_edges_path = Path(args.output_edges)

    if input_path.is_dir():
        input_files = [f for f in input_path.iterdir(
        ) if f.is_file() and f.suffix == ".tsv"]
    else:
        input_files = [input_path]

    node_headers = OrderedSet(["id:ID", ":LABEL", "name",
                    "curie_prefix", "curie_local_part"])
    edge_headers = OrderedSet([":START_ID", ":TYPE", ":END_ID"])

    for file in input_files:
        yaml_header,column_headers = get_sssom_tsv_headers(open(file, 'r'))
        edge_headers.update(column_headers)

    with open(output_nodes_path, "w", newline="", encoding="utf-8") as nodes_file, \
            open(output_edges_path, "w", newline="", encoding="utf-8") as edges_file:
        nodes_writer = csv.writer(nodes_file, delimiter="\t")
        edges_writer = csv.writer(edges_file, delimiter="\t")

        nodes_writer.writerow(node_headers)
        edges_writer.writerow(list(edge_headers))

        printed_node_ids = OrderedSet()
        node_ids_to_print = OrderedSet()  # nodes we need to print but didn't get a label for yet

        for file in input_files:
            write_mappings(file, nodes_writer, edges_writer,
                           printed_node_ids, node_ids_to_print, edge_headers)

        # Print nodes without labels
        for leftover_node_id in node_ids_to_print:
            print_node(leftover_node_id, leftover_node_id, nodes_writer)

def write_mappings(input_file, nodes_writer, edges_writer, printed_node_ids, node_ids_to_print, edge_headers):

    f = open(input_file, 'r')
    yaml_header,column_headers = get_sssom_tsv_headers(f)

    reader = csv.DictReader(f, delimiter='\t', fieldnames=column_headers)

    for line in reader:
        subj_id = line["subject_id"]
        subj_label = line["subject_label"]
        obj_id = line["object_id"]
        obj_label = line["object_label"]

        visit_node(subj_id, subj_label, nodes_writer, printed_node_ids, node_ids_to_print)
        visit_node(obj_id, obj_label, nodes_writer, printed_node_ids, node_ids_to_print)

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

def visit_node(node_id, node_label, nodes_writer, printed_node_ids, node_ids_to_print):
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
