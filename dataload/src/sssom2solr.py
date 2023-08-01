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
    parser.add_argument("--output-stats", required=True,
                        help="path for output solr jsonl stats file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_mappings_path = Path(args.output_mappings)
    output_mapping_sets_path = Path(args.output_mapping_sets)
    output_stats_path = Path(args.output_stats)

    if input_path.is_dir():
        input_files = [f for f in input_path.iterdir(
        ) if f.is_file() and f.suffix == ".tsv"]
    else:
        input_files = [input_path]

    output_mappings = open(output_mappings_path, "w", encoding="utf-8")
    output_mapping_sets = open(output_mapping_sets_path, "w", encoding="utf-8")
    output_stats = open(output_stats_path, "w", encoding="utf-8")

    total_num_mappings = 0
    all_distinct_entity_iris = set()
    
    for file in input_files:
        total_num_mappings += write_mappings(file, output_mappings, output_mapping_sets, all_distinct_entity_iris)
    
    output_stats.write(json.dumps({
        'num_mapping_sets': len(input_files),
        'num_mappings': total_num_mappings,
        'num_entities': len(all_distinct_entity_iris)
    }) + "\n")

    output_mappings.close()
    output_mapping_sets.close()
    output_stats.close()

def write_mappings(input_file, output_mappings, output_mapping_sets, all_distinct_entity_iris):

    f = open(input_file, 'r')
    yaml_header,column_headers = get_sssom_tsv_headers(f)

    curie_map = yaml_header['curie_map']

    entity_mapping_set_props = dict()
    if 'mapping_set_id' in yaml_header:
        entity_mapping_set_props['mapping_set_id'] = yaml_header['mapping_set_id']
    if 'mapping_set_group' in yaml_header:
        entity_mapping_set_props['mapping_set_group'] = yaml_header['mapping_set_group']

    # possible option if we need the entire header in results, but should be
    # excluded from indexing in solr config
    #
    #entity_mapping_set_props['mapping_set_header'] = json.dumps(yaml_header)

    num_mappings = 0
    distinct_entity_iris = set()

    reader = csv.DictReader(f, delimiter='\t', fieldnames=column_headers)

    for line in reader:
        line.update(entity_mapping_set_props)
        line['subject_iri'] = curie_to_iri(line['subject_id'], curie_map)
        line['predicate_iri'] = curie_to_iri(line['predicate_id'], curie_map)
        line['object_iri'] = curie_to_iri(line['object_id'], curie_map)
        line['entity_id'] = [line['subject_id'], line['object_id']]
        line['entity_iri'] = [line['subject_iri'], line['object_iri']]
        distinct_entity_iris.add(line['subject_iri'])
        distinct_entity_iris.add(line['object_iri'])
        output_mappings.write(json.dumps(line))
        output_mappings.write("\n")

    output_mapping_set = {}
    output_mapping_set.update(yaml_header)
    output_mapping_set.update({
        'num_mappings': num_mappings,
        'num_entities': len(distinct_entity_iris)
    })
    output_mapping_sets.write(json.dumps(output_mapping_set))
    output_mapping_sets.write("\n")

    all_distinct_entity_iris.update(distinct_entity_iris)
    return num_mappings


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
