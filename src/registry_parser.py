import argparse
import uuid
from typing import Tuple

import yaml
from pyld.jsonld import expand
from rdflib import Graph
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


def add_uuid_n_expand_curie(input) -> dict:
    input["@id"], input["uuid"] = generate_uuid([input["mapping_set_id"]])

    if not input.get("mappings"):
        return input

    context = get_context(input)

    for mapping in input["mappings"]:
        mapping_key = [
            mapping["subject_id"],
            mapping["predicate_id"],
            mapping["object_id"],
            mapping["mapping_justification"],
        ]
        mapping["@id"], mapping["uuid"] = generate_uuid(mapping_key)
        mapping["@type"] = "Mapping"

        mapping["subject_id"] = expand_curie(mapping["subject_id"], context)
        mapping["object_id"] = expand_curie(mapping["object_id"], context)
    return input


def get_context(input) -> dict:
    return input["@context"]


def expand_curie(curie, context):
    namespace = curie.split(":")[0]
    if "http" in namespace:
        return curie

    return curie.replace(f"{namespace}:", context[f"{namespace}"])


def read_mappings(config: str):
    registry = registry_parser(config)

    for _, mapping_set_ref in registry.mapping_set_references.items():  # type: ignore
        print(f"Parsing mapping_set_id {mapping_set_ref.mapping_set_id}")

        mapping_jsonld = update_context(
            add_uuid_n_expand_curie(to_json(parse_sssom_table(mapping_set_ref.mapping_set_id)))
        )

        context = get_context(mapping_jsonld)

        g = Graph()
        g.parse(data={"@graph": expand(mapping_jsonld, None)}, format="json-ld")  # type: ignore
        g.parse(data={"@context": context}, format="json-ld")  # type: ignore

        g.serialize(f"../data/monarch/{mapping_set_ref.local_name}.ttl", format="turtle")


def main(args):
    read_mappings(args.registry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", help="registry file with mappings")

    args = parser.parse_args()
    main(args)
