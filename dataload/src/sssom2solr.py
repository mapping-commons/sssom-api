import argparse
import json
import csv
from pathlib import Path
from sssom_stream import get_sssom_tsv_headers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="sssom tsv file or directory containing tsv files")
    parser.add_argument("--output-mappings", required=True,
                        help="path for output solr jsonl mappings file")
    parser.add_argument("--output-mapping-sets", required=True,
                        help="path for output solr jsonl mapping sets file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_mappings_path = Path(args.output_mappings)
    output_mapping_sets_path = Path(args.output_mapping_sets)

    if input_path.is_dir():
        input_files = [f for f in input_path.iterdir(
        ) if f.is_file() and f.suffix == ".tsv"]
    else:
        input_files = [input_path]

    output_mappings = open(output_mappings_path, "w", encoding="utf-8")
    output_mapping_sets = open(output_mapping_sets_path, "w", encoding="utf-8")
    
    for file in input_files:
        write_mappings(file, output_mappings, output_mapping_sets)
    
    output_mappings.close()
    output_mapping_sets.close()

def write_mappings(input_file, output_mappings, output_mapping_sets):

    f = open(input_file, 'r')
    yaml_header,column_headers = get_sssom_tsv_headers(f)

    output_mapping_sets.write(json.dumps(yaml_header))
    output_mapping_sets.write("\n")

    curie_map = yaml_header['curie_map']

    mapping_set_props = dict()
    if 'mapping_set_id' in yaml_header:
        mapping_set_props['mapping_set_id'] = yaml_header['mapping_set_id']
    if 'mapping_set_group' in yaml_header:
        mapping_set_props['mapping_set_group'] = yaml_header['mapping_set_group']

    # possible option if we need the entire header in results, but should be
    # excluded from indexing in solr config
    #
    #mapping_set_props['mapping_set_header'] = json.dumps(yaml_header)

    reader = csv.DictReader(f, delimiter='\t', fieldnames=column_headers)

    for line in reader:
        line.update(mapping_set_props)
        line['subject_iri'] = curie_to_iri(line['subject_id'], curie_map)
        line['predicate_iri'] = curie_to_iri(line['predicate_id'], curie_map)
        line['object_iri'] = curie_to_iri(line['object_id'], curie_map)
        line['entity_id'] = [line['subject_id'], line['object_id']]
        line['entity_iri'] = [line['subject_iri'], line['object_iri']]
        output_mappings.write(json.dumps(line))
        output_mappings.write("\n")

def curie_to_iri(curie, curie_map):
    if not ':' in curie:
        return ''
    prefix = curie[:curie.index(":")]
    local_part = curie[curie.index(":")+1:]
    if prefix in curie_map:
        iri_prefix = curie_map[prefix]
        return iri_prefix + local_part
    else:
        return ''

if __name__ == "__main__":
    main()
