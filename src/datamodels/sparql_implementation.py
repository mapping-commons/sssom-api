import hashlib
from tkinter.font import names
from typing import Union
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, OWL

from datamodel_interface import DataModel

class SparqlImpl(DataModel):
  
  def __init__(self, config: str):
    super.__init__(config)
    self.graph = Graph()

  def load_mappings(self):
    for mapping_set_df in self.msdfs:
      self._load_mapping_set(mapping_set_df)

  def get_mappings(self, curie: Union[str, None]):
    pass

  def serialize(self):
    return self.graph.serialize(destination="mappings.ttl")

  def _expand_curie(self, term, namespace):
    ns = term.split(":")[0]
    return str.replace(term, namespace[ns])

    
  def _generate_entity_id(namespace, input):
    m = hashlib.md5()
    m.update(input.encode('utf-8'))

    return URIRef(namespace + m.hexdigest())

  def _load_mapping_set(self, data):
    namespace = data.prefix_map
    map_set_id = self._generate_entity_id(namespace.sssom, data.metadata.mapping_set_id)
    self.graph.add((map_set_id, RDF.type, URIRef(namespace.sssom + "MappingSet")))
    self.graph.add((map_set_id, URIRef(namespace.sssom + "mapping_set_description"), Literal(data.metadata.mapping_set_description)))

    for mapping in data.df.itterows():
      map_id = self._load_mapping(map_set_id, mapping, namespace)
      self.graph.add((map_set_id, URIRef(namespace.sssom + "mapping"), map_id))


  def _load_mapping(self, data, namespace):
    map_id = self._generate_entity_id(namespace.sssom, data["subject_id"]+data["predicate_id"]+data["object_id"])
    self.graph.add((map_id, RDF.type, URIRef(namespace.sssom + "Mapping")))
    self.graph.add((map_id, URIRef(namespace.sssom + "subject_id"), URIRef(self._expand_curie(data["subject_id"], namespace))))
    self.graph.add((map_id, URIRef(namespace.sssom + "predicate_id"), URIRef(self._expand_curie(data["predicate_id"], namespace))))
    self.graph.add((map_id, URIRef(namespace.sssom + "object_id"), URIRef(self._expand_curie(data["object_id"], namespace))))

    return map_id
