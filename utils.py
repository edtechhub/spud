from django.db.models import Q
from django.conf import settings

import re


def formulate_with_filter_query(key):
	parts = settings.WITH_FILTERS[key]
	if type(parts) == str and (" AND " in parts or " OR " in parts):
		return join_with_filter_queries(key)

	if type(parts) == str:
		return Q(tak__iregex=parts)

	q_with = Q()
	for _q in parts["regex"]:
		q_with |= Q(tak__regex=_q)

	for _q in parts["iregex"]:
		q_with |= Q(tak__iregex=_q)

	return q_with

def join_with_filter_queries(key):
	query = settings.WITH_FILTERS[key]
	keys = query.replace(" AND ", " ").replace(" OR ", " ").replace("(", "").replace(")", "").split()

	complete_query = {}
	for _key in keys:
		complete_query[_key] = formulate_with_filter_query(_key)

	if key == "TT and PP":
		return ((complete_query["TT"]) & (complete_query["PP"]))
	elif key == "TE or (TT and PP)":
		return ((complete_query["TE"]) | (complete_query["TT"]) & (complete_query["PP"]))
	else:
		return Q()

def formulate_tak_query(query_string):
	query_parts = Q()

	for _q in query_string.split(" AND "):

		not_flag = re.findall("\s*NOT\s*", _q)
		_q = re.sub("\s*NOT\s*", "", _q)

		# remove single quote
		_q = re.sub("^\s*\'", "", _q)
		_q = re.sub("'\s*$", "", _q)

		# remove single quote
		_q = re.sub("^\s*\(\s*\'", "", _q)
		_q = re.sub("'\s*\)\s*$", "", _q)

		if not_flag:
			query_parts &= ~Q(tak__iregex=_q)
		else:
			query_parts &= Q(tak__iregex=_q)

	return query_parts
