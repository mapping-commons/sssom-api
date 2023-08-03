
import json
from math import ceil
import requests
from urllib.parse import urlencode
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

def create_paged_mappings_response(body, page, limit):
	#print(json.dumps(body))
	res = {
		'pagination': {
			'page_number': page,
			'total_items': body['response']['numFound'],
			'total_pages': ceil(float(body['response']['numFound'])/limit)
		},
		'data': body['response']['docs']
	}
	if 'facet_counts' in body:
		res['facets'] = body["facet_counts"]["facet_fields"]
	return res



def get_mappings(page:int, limit:int, filters:ImmutableMultiDict[str,str], facets:list[str], min_confidence = None, max_confidence = None):
	print(json.dumps(filters.to_dict()))
	params = [
		('defType', 'edismax'),
		('q', '*'),
		('qf', ''),
		('fq', encode_query(filters)),
		('start', (page-1) * limit),
		('rows', limit)
	]
	if len(facets) > 0:
		params.extend([
			('facet', 'true'),
			('facet.field', " ".join(facets)),
		])
	return create_paged_mappings_response(
		solr_select('sssom_mappings', params),
		page, limit
	)

def get_mapping_sets(page:int, limit:int, filters:ImmutableMultiDict[str,str], facets:list[str]):
	return create_paged_mappings_response(
		solr_select('sssom_mappings', [
			('defType', 'edismax'),
			('q', '*'),
			('qf', ''),
			('fq', encode_query(filters)),
			#('facet', 'true'),
			#('facet.field', " ".join(facets)),
			('start', (page-1) * limit),
			('rows', limit)
		]),
		page, limit
	)

def get_mapping_by_id(id:str):
	res = solr_select('ssssom_mappings', [
			('q', ImmutableMultiDict[str,str](
				('id', id)
			))
		])
	return res['response']['docs'][0]

def solr_stats():
	res = solr_select('sssom_stats', [
		('defType', 'edismax'),
		('q', '*'),
		('qf', ''),
		('start', '0'),
		('rows', '1'),
	]),
	return res['response']['docs'][0]

