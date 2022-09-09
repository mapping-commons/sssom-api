from typing import Iterable, Union

from rdflib import URIRef
from rdflib.namespace import OWL

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
from sssom.constants import SCHEMA_VIEW
from ..models import Mapping


class SparqlImpl(SparqlImplementation):
  def get_slot_uri(field: str) -> str:
    element_type = type(field)
    cn = element_type.class_name
    slot = SCHEMA_VIEW.induced_slot(field, cn)
    return SCHEMA_VIEW.get_uri(slot, expand=True)

  def default_query(self, field, value) -> SparqlQuery:
    query = SparqlQuery(
      select=["*"],
      where = []
    )
    return query

  def get_sssom_mapping_by_field(self, field: str, value: str) -> Iterable[Mapping]:
    pass
  
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

# def get_terms(mappings) -> Iterable[ResponseMapping]:
#   return (
#     ResponseMapping(
#       subject_id=m.subject_id,
#       predicate_id=m.predicate_id,
#       object_id=m.object_id,
#       mapping_justification=m.mapping_justification
#     )
#     for m in mappings
#   )

def get_mappings(imp: SparqlImpl, curie: CURIE) -> Iterable[Mapping]:
  mappings = imp.get_sssom_mappings_by_field(curie)
  return mappings

def get_mappings_field(imp: SparqlImpl, field: str, value: str) -> Iterable[Mapping]:
  mappings = imp.get_sssom_mapping_by_field(field, value)
  return mappings