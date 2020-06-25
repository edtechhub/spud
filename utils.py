from django.db.models import Q
from django.db import connection

import re


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


def faster_count():
    with connection.cursor() as cursor:
        cursor.execute("SELECT reltuples::bigint AS __count FROM pg_class WHERE relname = 'publications';")
        est_count = int(cursor.fetchone()[0])

    return est_count

