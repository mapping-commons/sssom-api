import argparse
import json
import csv
from pathlib import Path
from collections import defaultdict
from sssom_stream import get_sssom_tsv_headers

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

    printed_node_ids = OrderedSet()
    node_ids_to_print = OrderedSet()  # nodes we need to print but didn't get a label for yet

    with open(output_path, "w", encoding="utf-8") as output_file:
        for file in input_files:
            write_mappings(file, output_file, printed_node_ids, node_ids_to_print)

        # Print nodes without labels
        for leftover_node_id in node_ids_to_print:
            print_node(leftover_node_id, leftover_node_id, output_file)

def write_mappings(input_file, output_file, printed_node_ids, node_ids_to_print):

    f = open(input_file, 'r')
    yaml_header,column_headers = get_sssom_tsv_headers(f)

    reader = csv.DictReader(f, delimiter='\t', fieldnames=column_headers)

    for line in reader:
        subj_id = line["subject_id"]
        subj_label = line["subject_label"]
        obj_id = line["object_id"]
        obj_label = line["object_label"]
        visit_node(subj_id, subj_label, output_file, printed_node_ids, node_ids_to_print)
        visit_node(obj_id, obj_label, output_file, printed_node_ids, node_ids_to_print)

def visit_node(node_id, node_label, output_file, printed_node_ids, node_ids_to_print):
    if node_id in printed_node_ids or node_id in node_ids_to_print:
        return

    if not node_label:
        node_ids_to_print.add(node_id)
        return

    node_ids_to_print.discard(node_id)
    printed_node_ids.add(node_id)

    print_node(node_id, node_label, output_file)

def print_node(node_id, node_label, output_file):
    curie_prefix = node_id.split(":")[0]
    curie_local_part = node_id.split(":")[1]

    output_file.write(json.dumps({
        'node_id': node_id,
        'curie_prefix': curie_prefix,
        'curie_local_part': curie_local_part,
        'node_label': node_label
    }))
    output_file.write("\n")

if __name__ == "__main__":
    main()
