import argparse
import json
import uuid
from typing import List, Tuple

import yaml
from sssom.parsers import parse_sssom_table
from sssom.writers import to_json
from sssom_schema import SSSOM, MappingRegistry, MappingSetReference


def registry_parser(config: str) -> MappingRegistry:
    with open(config, "r") as f:
        data = yaml.safe_load(f)

    map_set_refs = (
        MappingSetReference(
            mapping_set_id=mapping["mapping_set_id"],
            mapping_set_group=mapping["mapping_set_group"],
        )
        for mapping in data["mapping_set_references"]
    )

    return MappingRegistry(
        mapping_registry_id=data["mapping_registry_id"],
        homepage=data["homepage"],
        mapping_set_references=list(map_set_refs),
    )


def generate_uuid(input) -> Tuple[str, str]:
    input_concat = "".join(input)
    id = uuid.uuid5(uuid.NAMESPACE_DNS, input_concat)
    uu_id = str(id).replace("-", "")

    return f"{SSSOM}{uu_id}", uu_id


def update_context(input: dict) -> dict:
    for _, value in input["@context"].items():
        if not isinstance(value, dict):
            continue

        if not value.get("@type"):
            continue

        if value["@type"] != "rdfs:Resource":
            continue

        value["@type"] = "@id"

    input["@context"]["uuid"] = {"@type": "xsd:string"}

    return input


def add_uuid(input) -> dict:
    input["@id"], input["uuid"] = generate_uuid([input["mapping_set_id"]])
    for mapping in input["mappings"]:
        mapping_key = [
            mapping["subject_id"],
            mapping["predicate_id"],
            mapping["object_id"],
            mapping["mapping_justification"],
        ]
        mapping["@id"], mapping["uuid"] = generate_uuid(mapping_key)
        mapping["@type"] = "Mapping"
    return input


def read_mappings(config: str) -> List[dict]:
    # mappings_graph = ConjunctiveGraph()
    mappings_json = []

    registry = registry_parser(config)

    for _, mapping_set_ref in registry.mapping_set_references.items():  # type: ignore
        print(f"Parsing mapping_set_id {mapping_set_ref.mapping_set_id}")
        # mappings_graph += to_rdf_graph(parse_sssom_table(mapping_set_ref.mapping_set_id))
        mappings_json.append(
            update_context(add_uuid(to_json(parse_sssom_table(mapping_set_ref.mapping_set_id))))
        )

    return mappings_json


def main(args):
    mappings_graph = read_mappings(args.registry)
    # mappings_graph.serialize("../data/mappings.ttl")
    with open("../data/mappings.jsonld", "w", encoding="utf-8") as f:
        json.dump(mappings_graph, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", help="registry file with mappings")

    args = parser.parse_args()
    main(args)
