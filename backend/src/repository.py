
from math import ceil
import requests
from urllib.parse import urlencode
from fastapi_pagination import Page
from starlette.datastructures import ImmutableMultiDict

import os
from .escape_query_chars import escape_query_chars

from .models import PaginationParams

SOLR_HOST = os.environ.get('SSSOM_SOLR_HOST')
if SOLR_HOST == None:
	SOLR_HOST = 'http://localhost:8983'


def solr_select(core, query_params):
	url = SOLR_HOST + '/solr/' + core + '/select?' + urlencode(query_params, doseq=True)
	print('solr: get ' + url)
	return requests.get(url).json()

def encode_query_value(key, values):
	return key + ":(" + ' OR '.join( ("\"" + escape_query_chars(v) + "\"") for v in values) + ")"

def encode_query(filters:ImmutableMultiDict[str,str]):
	fq = []
	for k in filters.keys():
		# todo move query splitting to controller
		if not k in ['min_confidence', 'max_confidence', 'entity_id', 'limit', 'page', 'facets']:
			fq.append(encode_query_value(k, filters.getlist(k)))
	return fq

def create_paged_mappings_response(body, pagination:PaginationParams):
	return {
		'pagination': {
			'page_number': pagination.page,
			'total_items': body['response']['numFound'],
			'total_pages': ceil(float(body['response']['numFound'])/pagination.limit)
		},
		'facets': body["facet_counts"]["facet_fields"],
		'data': body['response']['docs']
	}

def get_mappings(page:int, limit:int, filters:ImmutableMultiDict[str,str], facets:list[str], min_confidence = None, max_confidence = None):
	return create_paged_mappings_response(
		solr_select('sssom_mappings', [
			('defType', 'edismax'),
			('q', '*'),
			('qf', ''),
			('fq', encode_query(filters)),
			('facet', 'true'),
			('facet.field', " ".join(facets))
			('start', (pagination.page-1) * pagination.limit),
			('rows', pagination.limit)
		]),
		pagination
	)

def get_mapping_sets(page:int, limit:int, filters:ImmutableMultiDict[str,str], facets:list[str]):
	return create_paged_mappings_response(
		solr_select('sssom_mappings', [
			('defType', 'edismax'),
			('q', '*'),
			('qf', ''),
			('fq', encode_query(filters)),
			('facet', 'true'),
			('facet.field', " ".join(facets))
			('start', (pagination.page-1) * pagination.limit),
			('rows', pagination.limit)
		]),
		pagination
	)

def get_mapping_by_id(id:str):
	res = solr_select('ssssom_mappings', [
			('q', ImmutableMultiDict[str,str](
				('id', id)
			))
		])
	return res['response']['docs'][0]


def solr_stats():
	res = get_mappings(0, 1, ImmutableMultiDict(), ["id", "entity_iri", "mapping_set_id"])
	return {
		"numMappings": res["facets"]["id"],
		"numEntities": res["facets"]["entity_iri"],
		"numMappingSets": res["facets"]["mapping_set_id"],
	}

