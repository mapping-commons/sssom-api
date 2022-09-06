from typing import Iterable, Optional

from rdflib import Namespace
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

from ..models import Mapping, MappingSet

SSSOM = Namespace("https://w3id.org/sssom/")

class SparqlImpl(SparqlImplementation):
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

  def get_mapping_sets(self) -> Iterable[MappingSet]:
    query = SparqlQuery(
      select=["?mapping_set", "?id", "?license"],
      where=[f"?mapping_set <{RDF.type}> <{SSSOM.MappingSet}>",
             f"?mapping_set <{SSSOM.mapping_set_id}> ?id",
             f"?mapping_set <{DCTERMS.license}> ?license"],
    )
    bindings = self._query(query)
    for row in bindings:
      m = self.create_sssom_mapping_set(
        mapping_set_id=row['id']['value'],
        license=row['license']['value'])
      if m is not None:
        yield m

def get_mappings(imp: SparqlImpl, curie: str) -> Iterable[Mapping]:
  mappings = imp.get_sssom_mappings_by_curie(curie)
  return mappings

def get_mapping_sets(imp: SparqlImpl) -> Iterable[MappingSet]:
  mapping_sets = imp.get_mapping_sets()
  return mapping_sets
