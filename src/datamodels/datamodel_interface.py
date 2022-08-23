from typing import Union, List

from models import MappingSet
from sssom.util import MappingSetDataFrame
from ..parser import read_mappings

class DataModel():
  def __init__(self, config) -> None:
    self.msdfs: List[MappingSetDataFrame] = read_mappings(config)

  def load_mappings(self):
    pass

  def get_mappings(self, curie: Union[str, None]):
    pass
