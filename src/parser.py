import yaml
from typing import List

from sssom.util import MappingSetDataFrame
from sssom.parsers import parse_sssom_table
from models import MappingRegistry, MappingSetReference

def registry_parser(config: str):
  with open(config, 'r') as f:
    data = yaml.safe_load(f)

  map_set_refs = (MappingSetReference(
    mapping_set_id=mapping['mapping_set_id'],
    mapping_set_group=mapping['mapping_set_group'],
  ) 
  for mapping in data['mappings'])

  return (
    MappingRegistry(
      mapping_registry_id=data['registry_id'],
      homepage=data['homepage'],
      mapping_set_references=list(map_set_refs)
    )
  )

def read_mappings(config: str) -> List[MappingSetDataFrame]:
  msdfs = []
  FILE_FORMAT = ".sssom.tsv"
  BASE_URL = "https://raw.githubusercontent.com/mapping-commons/mh_mapping_initiative/master/mappings/"

  registry = registry_parser(config)

  for _, mapping_set_ref in registry.mapping_set_references.items():
    msdfs.append(parse_sssom_table(BASE_URL + mapping_set_ref.mapping_set_id + FILE_FORMAT))

  return msdfs
