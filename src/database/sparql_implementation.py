from typing import Iterable, List, Optional, Tuple, Union

from fastapi import Request
from oaklib.implementations.sparql.sparql_implementation import SparqlImplementation
from oaklib.implementations.sparql.sparql_query import SparqlQuery
from oaklib.utilities.mapping.sssom_utils import create_sssom_mapping
from rdflib.namespace._RDF import RDF
from sssom_schema import SSSOM, Mapping, MappingSet

from ..models import SearchEntity
from ..utils import OBO_CURIE_CONVERTER, parse_fields_type, sci2dec


class SparqlImpl(SparqlImplementation):
    def __post_init__(self, schema_view):
        super(SparqlImplementation, self).__post_init__()
        self.schema_view = schema_view

    def value_to_sparql(self, value: str) -> str:
        if value.startswith("http"):
            return f"<{value}>"
        elif ":" in value:
            return self.curie_to_sparql(value)
        else:
            return f'"{value}"'

    def get_slot_uri(self, field: str) -> str:
        if field == "uuid":
            return f"{SSSOM}uuid"
        if field == "mapping_set":
            return f"{SSSOM}mappings"
        else:
            return self.schema_view.view.get_uri(field, expand=True)

    def default_query(
        self,
        type: str,
        slots: set[str],
        subject: Union[str, None] = None,
        fields: Union[dict, None] = None,
        inverse: bool = False,
    ) -> SparqlQuery:
        query = SparqlQuery(
            select=["*"],
            where=[],
        )

        if subject is None:
            subject = "?_x"
        else:
            subject = f"<{subject}>"

        query.where.append(
            f"{subject} {self.value_to_sparql(RDF.type)} {self.value_to_sparql(type)}"
        )

        for f in slots:
            f_uri = self.get_slot_uri(f)
            opt = f"OPTIONAL {{ {subject} <{f_uri}> ?{f} }}"
            query.where.append(opt)

        if fields is not None:
            for field, values in fields.items():
                if field == "mapping_set":
                    filter = self.value_to_sparql(self.get_slot_uri(field))
                    if inverse:
                        query.where.append(f"OPTIONAL {{ ?{field} {filter} {subject} }}")

                if values is not None:
                    values = list(map(lambda x: self.value_to_sparql(x), values))
                    query.add_filter(f'?{field} IN ( {", ".join(values)})')

        return query

    def add_filters(
        self, query: SparqlQuery, filter: Union[List[dict], None] = None
    ) -> SparqlQuery:
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
                query.add_filter(f"CONTAINS(STR(?{f['field']}), '{f['value']}')")

        return query

    def transform_result(self, row: dict) -> dict:
        result = {}

        for k, v in row.items():
            if v["value"] == "None":
                result[k] = None
            elif "confidence" in k:
                result["confidence"] = sci2dec(v["value"])
            else:
                result[k] = v["value"]
        return result

    def transform_result_list(self, results):
        # sparql results in one list
        out = []
        for row in results:
            for _, v in row.items():
                out.append(v["value"])
        return out

    def _get_fields(self, slots_type: List) -> Tuple[set, set]:
        fields_list, fields_single = parse_fields_type(
            multivalued_fields=self.schema_view.multivalued_slots.copy(), slots=slots_type
        )
        fields_single.add("uuid")

        return fields_list, fields_single

    def get_mappings_by_field(self, fields: dict) -> Iterable[dict]:
        fields_list, fields_single = self._get_fields(
            slots_type=self.schema_view.mapping_slots.copy()
        )
        # Search for single value attributes
        default_query = self.default_query(
            type=Mapping.class_class_uri, slots=fields_single, fields=fields
        )
        bindings = self._query(default_query)
        for row in bindings:
            r = self.transform_result(row)
            # Search for multiple value attributes
            for field in fields_list:
                default_query_list = self.default_query(
                    type=Mapping.class_class_uri, slots={field}, subject=r["_x"], fields=fields
                )
                results = self._query(default_query_list)
                bindings_list = self.transform_result_list(results)
                if len(bindings_list):
                    r[f"{field}"] = bindings_list
            yield r

    def get_sssom_mappings_by_field(self, fields: dict) -> Iterable[Mapping]:
        bindings = self.get_mappings_by_field(fields)
        for row in bindings:
            r = self.transform_result(row)
            r.pop("_x")
            r.pop("uuid")
            m = create_sssom_mapping(**r)
            if m is not None:
                yield m

    def create_sssom_mapping_set(self, mapping_set_id: str, **kwargs) -> Optional[MappingSet]:
        return MappingSet(mapping_set_id=mapping_set_id, **kwargs)

    def get_sssom_mappings_by_curie(self, search_filter: SearchEntity) -> Iterable[Mapping]:
        filters = search_filter.dict()
        curies = filters.pop("curies")

        filters["subject_id"] = [OBO_CURIE_CONVERTER.expand(curie) for curie in curies]
        bindings = self.get_sssom_mappings_by_field(filters)
        for m in bindings:
            yield m

        filters.pop("subject_id")
        filters["object_id"] = [OBO_CURIE_CONVERTER.expand(curie) for curie in curies]
        bindings = self.get_sssom_mappings_by_field(filters)
        for m in bindings:
            yield m

    def get_ui_mappings_by_curie(self, search_filter: SearchEntity) -> Iterable[dict]:
        filters = search_filter.dict()
        curies = filters.pop("curies")

        filters["subject_id"] = [OBO_CURIE_CONVERTER.expand(curie) for curie in curies]
        bindings = self.get_mappings_by_field(filters)
        for row in bindings:
            row.pop("_x")
            row["subject_id_curie"] = OBO_CURIE_CONVERTER.compress(row["subject_id"])
            row["object_id_curie"] = OBO_CURIE_CONVERTER.compress(row["object_id"])
            yield row

        filters.pop("subject_id")
        filters["object_id"] = [OBO_CURIE_CONVERTER.expand(curie) for curie in curies]
        bindings = self.get_mappings_by_field(filters)
        for row in bindings:
            row.pop("_x")
            row["subject_id_curie"] = OBO_CURIE_CONVERTER.compress(row["subject_id"])
            row["object_id_curie"] = OBO_CURIE_CONVERTER.compress(row["object_id"])
            yield row

    def get_mappings_by_filter(self, filter: Union[List[dict], None]) -> Iterable[dict]:
        fields_list, fields_single = self._get_fields(
            slots_type=self.schema_view.mapping_slots.copy()
        )
        # Search for single value attributes
        default_query = self.add_filters(
            self.default_query(
                type=Mapping.class_class_uri,
                slots=fields_single,
            ),
            filter,
        )
        bindings = self._query(default_query)
        for row in bindings:
            r = self.transform_result(row)
            # Search for multiple value attributes
            for field in fields_list:
                default_query_list = self.add_filters(
                    self.default_query(
                        type=Mapping.class_class_uri,
                        slots={field},
                        subject=r["_x"],
                    ),
                    filter,
                )
                results = self._query(default_query_list)
                bindings_list = self.transform_result_list(results)
                if len(bindings_list):
                    r[f"{field}"] = bindings_list
            r.pop("_x")
            yield r

    def get_sssom_mappings_by_filter(self, filter: Union[List[dict], None]) -> Iterable[Mapping]:
        bindings = self.get_mappings_by_filter(filter)
        for row in bindings:
            row.pop("uuid")
            m = create_sssom_mapping(**row)
            if m is not None:
                yield m

    def get_sssom_mapping_sets_query(
        self, request: Request, filter: Union[List[dict], None]
    ) -> Iterable[dict]:
        fields_list, fields_single = parse_fields_type(
            multivalued_fields=self.schema_view.multivalued_slots,
            slots=self.schema_view.mapping_set_slots.copy(),
        )
        fields_single.add("uuid")
        # Search for single value attributes
        default_query = self.add_filters(
            self.default_query(type=MappingSet.class_class_uri, slots=fields_single), filter
        )
        bindings = self._query(default_query)
        for row in bindings:
            r = self.transform_result(row)
            # Search for multiple value attributes
            for field in fields_list:
                if field != "mappings":
                    default_query_list = self.default_query(
                        type=MappingSet.class_class_uri, slots={field}, subject=r["_x"]
                    )
                    bindings_list = self.transform_result_list(self._query(default_query_list))
                    r[f"{field}"] = bindings_list

            r["mappings"] = {"href": request.url_for(name="mappings_by_mapping_set", id=r["uuid"])}
            r.pop("_x")
            yield r

    def get_mapping_by_id(self, id: str) -> dict:
        fields_list, fields_single = self._get_fields(
            slots_type=self.schema_view.mapping_slots.copy()
        )
        # Search for single value attributes
        default_query = self.default_query(
            type=Mapping.class_class_uri, slots=fields_single, subject=f"{SSSOM}{id}"
        )
        bindings = self._query(default_query)[0]

        r = self.transform_result(bindings)
        # Search for multiple value attributes
        for field in fields_list:
            default_query_list = self.default_query(
                type=Mapping.class_class_uri, slots={field}, subject=f"{SSSOM}{id}"
            )
            results = self._query(default_query_list)
            bindings_list = self.transform_result_list(results)
            if len(bindings_list):
                r[f"{field}"] = bindings_list

        return r

    def get_sssom_mapping_by_id(self, id: str) -> Optional[Mapping]:
        mapping = self.get_mapping_by_id(id)
        mapping.pop("uuid")
        return create_sssom_mapping(**mapping)

    def get_sssom_mappings_by_mapping_set_id(self, id: str) -> Iterable[Mapping]:
        fields = {"mapping_set": f"{SSSOM}{id}"}
        default_query = self.default_query(
            type=Mapping.class_class_uri,
            slots=self.schema_view.mapping_slots.copy().append("mapping_set"),
            fields=fields,
            inverse=True,
        )
        bindings = self._query(default_query)
        for row in bindings:
            r = self.transform_result(row)
            r.pop("_x")
            m = create_sssom_mapping(**r)
            if m is not None:
                yield m

    def get_stats(self) -> dict:
        query = SparqlQuery(
            select=[
                """
                (COUNT(DISTINCT ?mapping) as ?nb_mapping)
                (COUNT(DISTINCT ?mapping_set) as ?nb_mapping_set)
                (COUNT(DISTINCT ?mapping_provider) as ?nb_mapping_provider)
                (COUNT(DISTINCT ?entity) as ?nb_entity)
                """
            ],
            where=[],
        )
        mappingset_uri = MappingSet.class_class_uri
        mapping_uri = Mapping.class_class_uri

        query.where.append(
            f"?mapping_set {self.value_to_sparql(RDF.type)} {self.value_to_sparql(mappingset_uri)}"
        )
        query.where.append(
            f"?mapping {self.value_to_sparql(RDF.type)} {self.value_to_sparql(mapping_uri)}"
        )
        query.where.append(
            f"?_x {self.value_to_sparql(self.get_slot_uri('mapping_provider'))} ?mapping_provider"
        )
        bindings = self._query(query)
        results = self.transform_result(bindings[0])

        # Splitting the query for efficiency (get results faster)
        query = SparqlQuery(
            select=["(COUNT(DISTINCT ?entity) as ?nb_entity)"],
            where=[],
        )
        clauses_entity = [
            f"?_y {self.value_to_sparql(self.get_slot_uri(pred))} ?entity"
            for pred in ["subject_id", "object_id"]
        ]
        query.where.append(" UNION ".join([f"{{ {clause} }}" for clause in clauses_entity]))
        bindings = self._query(query)
        results.update(self.transform_result(bindings[0]))
        return results


def get_mappings(imp: SparqlImpl, search_filter: SearchEntity) -> Iterable[Mapping]:
    mappings = imp.get_sssom_mappings_by_curie(search_filter)
    return mappings


def get_mappings_ui(imp: SparqlImpl, curies: SearchEntity) -> Iterable[dict]:
    mappings = imp.get_ui_mappings_by_curie(curies)
    return mappings


def get_mappings_field(imp: SparqlImpl, field: str, value: str) -> Iterable[Mapping]:
    filters = {f"{field}": value}
    mappings = imp.get_sssom_mappings_by_field(filters)
    return mappings


def get_mappings_query(imp: SparqlImpl, filter: Union[List[dict], None]) -> Iterable[Mapping]:
    mappings = imp.get_sssom_mappings_by_filter(filter)
    return mappings


def get_mappings_by_filter_ui(imp: SparqlImpl, filter: Union[List[dict], None]) -> Iterable[dict]:
    mappings = imp.get_mappings_by_filter(filter)
    for m in mappings:
        m["subject_id_curie"] = OBO_CURIE_CONVERTER.compress(m["subject_id"])
        m["object_id_curie"] = OBO_CURIE_CONVERTER.compress(m["object_id"])
        yield m


def get_mapping_sets(
    request: Request, imp: SparqlImpl, filter: Union[List[dict], None]
) -> Iterable[dict]:
    mapping_sets = imp.get_sssom_mapping_sets_query(request, filter)
    return mapping_sets


def get_mapping_by_id(imp: SparqlImpl, id: str) -> Optional[Mapping]:
    mapping = imp.get_sssom_mapping_by_id(id)
    return mapping


def get_ui_mapping_by_id(imp: SparqlImpl, id: str) -> dict:
    mapping = imp.get_mapping_by_id(id)
    mapping["subject_id_curie"] = OBO_CURIE_CONVERTER.compress(mapping["subject_id"])
    mapping["object_id_curie"] = OBO_CURIE_CONVERTER.compress(mapping["object_id"])

    return mapping


def get_mappings_by_mapping_set(imp: SparqlImpl, id: str) -> Iterable[Mapping]:
    mappings = imp.get_sssom_mappings_by_mapping_set_id(id)
    return mappings


def get_stats(imp: SparqlImpl) -> dict:
    stats = imp.get_stats()
    return stats
