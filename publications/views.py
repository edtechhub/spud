from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import connection
from .models import Publication
from django.views.decorators.http import require_http_methods

from django.conf import settings
from utils import *
import time

def raw_query(author, year, tak, filters = None):
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
				query = query + """ OR """ + """publications.""" + str(_filter) + """ >'0'"""
		else:
			for _filter in filters:
				query = query + """ OR """ + """publications.""" + str(_filter) + """ >'0'"""
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

	if counter == 0:
		return Publication.objects.all()
	query = query + """ ORDER BY year DESC"""

	return Publication.objects.raw(query)


def authenticate_user(function):
	def wrapper(request, *args, **kwargs):
		auth = request.GET.get('auth', request.POST.get('auth', '')).strip()
		if (not auth) or (auth != settings.AUTH_KEY):
			return HttpResponse('401 Unauthorized', status=401)
		return function(request, *args, **kwargs)

	return wrapper

@require_http_methods(["GET"])
@authenticate_user
def index(request):
	start = time.time()

	auth = request.GET.get('auth', '')

	year = request.GET.get('year', '').strip()
	tak = request.GET.get('tak', '').strip()
	author = request.GET.get('author', '').strip()
	form_f = request.GET.getlist('F filter')
	form_gc = request.GET.getlist('GC filter')
	form_gd = request.GET.getlist('GD filter')
	form_gr = request.GET.getlist('GR filter')
	form_o = request.GET.getlist('O filter')
	form_p1 = request.GET.getlist('P1 filter')
	form_p2 = request.GET.getlist('P2 filter')
	form_r = request.GET.getlist('R filter')
	form_te = request.GET.getlist('TE filter')
	form_tt = request.GET.getlist('TT filter')

	search_engine = request.GET.get('search-engine', 'off')
	highlight_param = request.GET.get('highlight', 'on')
	highlight_keywords = True if highlight_param == "on" else False

	filters = []
	#filters = form_f + form_gc + form_gd + form_gr + form_o + form_p1 + form_p2 + form_r + form_te + form_tt


	if search_engine == 'off':
		publications_list = raw_query(author, year, tak, filters)
	else:
		q_year = q_tak = q_with = Q()
		if year: q_year = Q(year=year)

		if tak: q_tak = formulate_tak_query(tak)

		publications_list = Publication.objects.filter(q_year & (q_tak)).order_by('-year')


	total_records = faster_count()

	per_page = request.GET.get('limit', 50)
	if int(per_page) == 0:
		publications = publications_list.all()
		q__q = connection.queries[-1]["sql"]

		total_matched_records = len(publications)
	else:
		paginator = Paginator(publications_list, per_page)
		page_number = request.GET.get('page')
		publications = paginator.get_page(page_number)

		q__q = connection.queries[-1]["sql"]

		total_matched_records = publications.paginator.count

	context = {
		'publications': publications,
		'total_records': total_records,
		'total_matched_records': total_matched_records,
		'year': year,
		'tak': tak,
		'author': author,
		'limit': per_page,

		'form_f': form_f,
		'FORM_F': settings.FORM_F,
		'form_gc': form_gc,
		'FORM_GC': settings.FORM_GC,
		'form_gd': form_gd,
		'FORM_GD': settings.FORM_GD,
		'form_gr': form_gr,
		'FORM_GR': settings.FORM_GR,
		'form_o': form_o,
		'FORM_O': settings.FORM_O,
		'form_p1': form_p1,
		'FORM_P1': settings.FORM_P1,
		'form_p2': form_p2,
		'FORM_P2': settings.FORM_P2,
		'form_r': form_r,
		'FORM_R': settings.FORM_R,
		'form_te': form_te,
		'FORM_TE': settings.FORM_TE,
		'form_tt': form_tt,
		'FORM_TT': settings.FORM_TT,


		'ABSTRACT_WORDS_LIMIT': settings.ABSTRACT_WORDS_LIMIT,
		'highlight_param': highlight_param,
		'highlight_keywords': highlight_keywords,


		'auth': settings.AUTH_KEY,
		'q__q': q__q,
		'timer': str(round(time.time() - start, 2)),

	}
	return render(request, 'publications/index.html', context)

@require_http_methods(["GET"])
@authenticate_user
def showrecord(request):
	auth = request.GET.get('auth', '')

	publication_id = request.GET.get('id')
	publication = Publication.objects.filter(id=publication_id).first()

	highlight_param = request.GET.get('highlight', 'on')
	highlight_keywords = True if highlight_param == "on" else False

	context = {
		'publication': publication,
		'highlight_keywords': highlight_keywords,

		'auth': settings.AUTH_KEY,
	}

	return render(request, 'publications/showrecord.html', context)

@require_http_methods(["POST"])
@authenticate_user
def ris_export(request):
	auth = request.POST.get('auth', '');

	publication_id = request.POST.get('id')
	publication = Publication.objects.filter(id=publication_id).first()

	response = HttpResponse(publication.ris_format(), content_type="application/x-research-info-systems")
	response['Content-Disposition'] = 'attachment; filename="{0}{1}.ris"'.format(publication.id, publication.year)

	return response

@require_http_methods(["POST"])
@authenticate_user
def zotero_export(request):
	auth = request.POST.get('auth', '');

	publication_ids = request.POST.getlist('ids[]')
	publications = Publication.objects.filter(id__in=publication_ids)

	zotero_content = "\n\n".join([publication.ris_format() for publication in publications])

	response = HttpResponse(zotero_content, content_type="application/x-research-info-systems")
	response['Content-Disposition'] = 'attachment; filename="zotero.ris"'

	return response

@require_http_methods(["GET"])
@authenticate_user
def keywords(request):
	auth = request.GET.get('auth', '');

	return JsonResponse({'countries': settings.COUNTRIES, 'regions': settings.REGIONS, 'development_terms': settings.DEVELOPMENT_TERMS})
