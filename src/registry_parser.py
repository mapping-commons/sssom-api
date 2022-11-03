
import argparse
from parser import read_mappings

def main(args):
  mappings_graph = read_mappings(args.registry)
  return mappings_graph.serialize("../data/mappings.ttl")

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('registry', help='registry file with mappings')

  args = parser.parse_args()
  main(args)