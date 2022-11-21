
import argparse, json, yaml

from rdflib import ConjunctiveGraph
from sssom.parsers import parse_sssom_table
from sssom.writers import to_rdf_graph, to_json
from models import MappingRegistry, MappingSetReference

def registry_parser(config: str) -> MappingRegistry:
  with open(config, 'r') as f:
    data = yaml.safe_load(f)

  map_set_refs = (MappingSetReference(
    mapping_set_id=mapping['mapping_set_id'],
    mapping_set_group=mapping['mapping_set_group']
  ) 
  for mapping in data['mapping_set_references'])

  return (
    MappingRegistry(
      mapping_registry_id=data['mapping_registry_id'],
      homepage=data['homepage'],
      mapping_set_references=list(map_set_refs)
    )
  )

def read_mappings(config: str) -> ConjunctiveGraph:
  # mappings_graph = ConjunctiveGraph()
  mappings_json = []

  registry = registry_parser(config)

  for _, mapping_set_ref in registry.mapping_set_references.items():
    print(f"Parsing mapping_set_id {mapping_set_ref.mapping_set_id}")
    # mappings_graph += to_rdf_graph(parse_sssom_table(mapping_set_ref.mapping_set_id))
    mappings_json.append(to_json(parse_sssom_table(mapping_set_ref.mapping_set_id)))
    
  return mappings_json

def main(args):
  mappings_graph = read_mappings(args.registry)
  # mappings_graph.serialize("../data/mappings.ttl")
  with open("../data/mappings.json", 'w', encoding='utf-8') as f:
    json.dump(mappings_graph, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('registry', help='registry file with mappings')

  args = parser.parse_args()
  main(args)