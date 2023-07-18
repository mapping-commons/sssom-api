
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

def encode(values:list[str]):
	return "(" + ' OR '.join(values.map(lambda v: "\"" + escape_query_chars(v) + "\"")) + ")"

def encode_query_value(key, values):
	return map(values, lambda v: key + ":" + encode(v))

def encode_query(filters:ImmutableMultiDict[str,str]):
	fq = []
	for k in filters.keys():
		fq.append(encode_query_value(k, filters.getlist(k)))
	return fq

def create_paged_mappings_response(body, pagination:PaginationParams):
	return {
		'pagination': {
			'page_number': pagination.page,
			'total_items': body['response']['numFound'],
			'total_pages': ceil(float(body['response']['numFound'])/pagination.limit)
		},
		'facets': {
			'mapping_justification': body['facet_counts']['facet_fields'].get('mapping_justification', {}),
			'predicate_id': body['facet_counts']['facet_fields'].get('predicate_id', {}),
			'confidence': {} # TODO
		},
		'data': body['response']['docs']
	}

def get_mappings(pagination:PaginationParams, filters:ImmutableMultiDict[str,str], min_confidence = None, max_confidence = None):
	return create_paged_mappings_response(
		solr_select('sssom_mappings', [
			('defType', 'edismax'),
			('q', '*'),
			('qf', ''),
			('fq', encode_query(filters)),
			('facet', 'true'),
			('facetFields', ['mapping_justification', 'predicate_id']),
			('start', pagination.page * pagination.limit),
			('rows', pagination.limit)
		]),
		pagination
	)


def get_mappings_by_id(id:str):
	res = solr_select('ssssom_mappings', [
			('q', ImmutableMultiDict[str,str](
				('id', id)
			))
		])
	return res['response']['docs'][0]

