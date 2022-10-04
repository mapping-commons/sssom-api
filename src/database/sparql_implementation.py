from typing import Iterable, List, Optional, Union

from rdflib import URIRef, Namespace
from rdflib.namespace import OWL, RDF, DCTERMS

from oaklib.implementations.sparql.abstract_sparql_implementation import _sparql_values
from oaklib.utilities.mapping.sssom_utils import create_sssom_mapping
from oaklib.implementations.sparql.sparql_implementation import SparqlImplementation
from oaklib.implementations.sparql.sparql_query import SparqlQuery
from oaklib.types import CURIE
from oaklib.datamodels.vocabulary import (
    ALL_MATCH_PREDICATES,
    EQUIVALENT_CLASS
)
from oaklib.resource import OntologyResource

from sssom_schema import SSSOM
from sssom.constants import SCHEMA_VIEW, MAPPING_SLOTS, MAPPING_SET_SLOTS
from ..models import Mapping, MappingSet

SSSOM = Namespace("https://w3id.org/sssom/")

class SparqlImpl(SparqlImplementation):
  def value_to_sparql(self, value: str) -> str:
    if value.startswith("http"):
      return f"<{value}>"
    elif ":" in value:
      return self.curie_to_sparql(value)
    else:
      return value

  def get_slot_uri(self, field: str) -> str:
    return SCHEMA_VIEW.get_uri(field, expand=True)
    
  def default_query(self, slots: List, field: Union[str, None]=None, value: Union[str, None]=None) -> SparqlQuery:
    query = SparqlQuery(
      select=["*"],
      where = []
    )

    if field != None and value != None:
      filter = self.get_slot_uri(field)
      query.where.append(f"?_x <{filter}> {self.value_to_sparql(value)}")
      slots.remove(field)
    
    for f in slots:
      f_uri = self.get_slot_uri(f)
      opt = f"OPTIONAL {{?_x <{f_uri}> ?{f}}}"
      query.where.append(opt)

    return query

  def add_filters(self, query: SparqlQuery, filter: Union[List[dict], None]=None) -> SparqlQuery:
    if filter is None:
      return query

    for f in filter:
      if f["operator"] == "ge":
        query.add_filter(f"?{f['field']} >= {f['value']}")
      if f["operator"] == "gt":
        query.add_filter(f"?{f['field']} > {f['value']}")
      if f["operator"] == "le":
        query.add_filter(f"?{f['field']} <= {f['value']}")
      if f["operator"] == "lt":
        query.add_filter(f"?{f['field']} < {f['value']}")
      if f["operator"] == "contains":
        query.add_filter(f"CONTAINS(?{f['field']}, '{f['value']}')")
    
    return query

  def transform_result(self, row: dict) -> dict:
    result = {}

    for k, v in row.items():
      if k != "_x":
        if v["value"] == 'None':
          result[k] = None
        else:
          result[k] = v["value"]
    print(result)
    return result

  def get_sssom_mappings_by_field(self, field: str, value: str) -> Iterable[Mapping]:
    bindings = self._query(self.default_query(MAPPING_SLOTS, field, value))
    for row in bindings:
      r = self.transform_result(row)
      r[f"{field}"] = value
      m = create_sssom_mapping(**r)
      if m is not None:
        yield m

  def create_sssom_mapping_set(self, mapping_set_id: str, **kwargs) -> Optional[MappingSet]:
    return MappingSet(mapping_set_id=mapping_set_id, **kwargs)

  def get_sssom_mappings_by_curie(self, curie: CURIE) -> Iterable[Mapping]:
    pred_uris = [self.curie_to_sparql(pred) for pred in ALL_MATCH_PREDICATES + [EQUIVALENT_CLASS]]
    query = SparqlQuery(
      select=["?p", "?o", "?j"],
      where=[f"?_x <{OWL.annotatedSource}> {self.curie_to_sparql(curie)}",
        f"?_x <{OWL.annotatedProperty}> ?p",
        f"?_x <{OWL.annotatedTarget}> ?o",
        f"?_x <{SSSOM.mapping_justification}> ?j",
        _sparql_values("p", pred_uris)],
    )
    bindings = self._query(query)
    for row in bindings:
      m = create_sssom_mapping(
        subject_id=curie,
        predicate_id=self.uri_to_curie(row["p"]["value"]),
        object_id=self.uri_to_curie(row["o"]["value"]),
        mapping_justification=row["j"]["value"],
      )
      if m is not None:
        yield m
    query = SparqlQuery(
        select=["?s", "?p"],
        where=[f"?_x <{OWL.annotatedSource}> ?s",
          f"?_x <{OWL.annotatedProperty}> ?p",
          f"?_x <{OWL.annotatedTarget}> {self.curie_to_sparql(curie)}",
          f"?_x <{SSSOM.mapping_justification}> ?j",
          _sparql_values("p", pred_uris)],
    )
    bindings = self._query(query)
    for row in bindings:
      m = create_sssom_mapping(
        subject_id=self.uri_to_curie(row["s"]["value"]),
        predicate_id=self.uri_to_curie(row["p"]["value"]),
        object_id=curie,
        mapping_justification=row["j"]["value"],
      )
      if m is not None:
        yield m

  def get_sssom_mappings_query(self, filter: Union[List[dict], None]) -> Iterable[Mapping]:
    default_query = self.add_filters(self.default_query(MAPPING_SLOTS), filter)
    
    bindings = self._query(default_query)
    for row in bindings:
      r = self.transform_result(row)
      m = create_sssom_mapping(**r)
      if m is not None:
        yield m
    
  def get_sssom_mapping_sets_query(self, filter: Union[List[dict], None]) -> Iterable[MappingSet]:
    default_query = self.add_filters(self.default_query(MAPPING_SET_SLOTS), filter)
    print(default_query.query_str())
    bindings = self._query(default_query)
    for row in bindings:
      r = self.transform_result(row)
      m = self.create_sssom_mapping_set(**r)
      if m is not None:
        yield m

def get_mappings(imp: SparqlImpl, curie: CURIE) -> Iterable[Mapping]:
  mappings = imp.get_sssom_mappings_by_curie(curie)
  return mappings

def get_mappings_field(imp: SparqlImpl, field: str, value: str) -> Iterable[Mapping]:
  mappings = imp.get_sssom_mappings_by_field(field, value)
  return mappings

def get_mappings_query(imp: SparqlImpl, filter: Union[List[dict], None]) -> Iterable[Mapping]:
  mappings = imp.get_sssom_mappings_query(filter)
  return mappings

def get_mapping_sets(imp: SparqlImpl, filter: Union[List[dict], None]) -> Iterable[MappingSet]:
  mapping_sets = imp.get_sssom_mapping_sets_query(filter)
  return mapping_sets
