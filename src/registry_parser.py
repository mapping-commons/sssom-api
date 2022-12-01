
import argparse, json, yaml, uuid

from rdflib import ConjunctiveGraph
from sssom.parsers import parse_sssom_table
from sssom.writers import to_rdf_graph, to_json
from models import MappingRegistry, MappingSetReference
from sssom_schema import SSSOM

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

def generate_uuid(input):
  input_concat = ''.join(input)
  id = uuid.uuid5(uuid.NAMESPACE_DNS, input_concat)
  
  return f'{SSSOM}{str(id).replace("-", "")}'

def update_context(input: dict) -> dict:
  for _, value in input["@context"].items():
    if not isinstance(value, dict):
      continue
    
    if not value.get('@type'):
      continue

    if value['@type'] != "rdfs:Resource":
      continue
    
    value['@type'] = "@id"

  return input

def add_uuid(input):
  input["@id"] = generate_uuid([input["mapping_set_id"]])
  for mapping in input["mappings"]:
    mapping_key = [mapping["subject_id"], mapping["predicate_id"], mapping["object_id"], mapping["mapping_justification"]]
    mapping["@id"] = generate_uuid(mapping_key)
    mapping["@type"] = "Mapping"
  return input

def read_mappings(config: str) -> ConjunctiveGraph:
  # mappings_graph = ConjunctiveGraph()
  mappings_json = []

  registry = registry_parser(config)

  for _, mapping_set_ref in registry.mapping_set_references.items():
    print(f"Parsing mapping_set_id {mapping_set_ref.mapping_set_id}")
    # mappings_graph += to_rdf_graph(parse_sssom_table(mapping_set_ref.mapping_set_id))
    mappings_json.append(update_context(add_uuid(to_json(parse_sssom_table(mapping_set_ref.mapping_set_id)))))
    # mappings_json.append(add_uuid(to_json(parse_sssom_table(mapping_set_ref.mapping_set_id))))
    # mappings_json.append(to_json(parse_sssom_table(mapping_set_ref.mapping_set_id)))
    
  return mappings_json

def main(args):
  mappings_graph = read_mappings(args.registry)
  # mappings_graph.serialize("../data/mappings.ttl")
  with open("../data/mappings.jsonld", 'w', encoding='utf-8') as f:
    json.dump(mappings_graph, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('registry', help='registry file with mappings')

  args = parser.parse_args()
  main(args)