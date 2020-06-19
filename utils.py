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


def raw_query(author, filters, year, tak):
	query = """SELECT publications.id, publications.title, publications.additionaltitles, publications.authors, publications.year, publications.publicationtype, publications.links, publications.importedfrom, publications.containername, publications.doi, publications.tsv, publications.recordmetadata_zbuamajorversion, publications.recordmetadata_dateretrieved, publications.recordmetadata_dateconverted, publications.recordmetadata_recordtype, publications.recordmetadata_source, publications.recordmetadata_recordname, publications.recordmetadata_searchguid, publications.recordmetadata_numberinsource, publications.recordmetadata_zbuaminorversion, publications.publisherdatecopyright, publications.location, publications.author100, publications.daterange, publications.isbn, publications.citation, publications.keywords, publications.abstract, publications.identifier, publications.itemdatatype, publications.itemdatahandler, publications.created_at FROM publications WHERE """
	counter = 0
	if author:
		counter += 1
		query = query + """publications.tsa @@ websearch_to_tsquery('""" + str(author) + """')"""

	if filters:
		counter += 1
		if counter == 1:
			query = query + """publications.""" + str(filters[0]) + """ >'0'"""
			for _filter in filters:
				query = query + """ AND """ + """publications.""" + str(_filter) + """ >'0'"""
		else:
			for _filter in filters:
				query = query + """ AND """ + """publications.""" + str(_filter) + """ >'0'"""
	if year:
		counter += 1
		if counter == 1:
			query = query + """publications.year='""" + str(year) + """'"""
		else:
			query = query + """ AND """ + """publications.year ='""" + str(year) + """'"""
	if tak:
		counter += 1
		if counter == 1:
			query = query + """publications.tsv @@ websearch_to_tsquery('""" + str(tak) + """')"""
		else:
			query = query + """ AND """ + """publications.tsv @@ websearch_to_tsquery('""" + str(tak) + """')"""

	query = query + """ ORDER BY year DESC"""

	return query
