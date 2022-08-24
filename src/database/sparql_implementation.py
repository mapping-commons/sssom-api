from typing import Iterable, Union
from rdflib import Graph
from oaklib.implementations.sparql.sparql_implementation import SparqlImplementation
from oaklib.resource import OntologyResource

from ..models import Mapping

class SparqlImpl(SparqlImplementation):
  pass

def get_mappings(imp: SparqlImpl, curie: Union[str, None]) -> Iterable[Mapping]:
  return imp.get_sssom_mappings_by_curie(curie)




