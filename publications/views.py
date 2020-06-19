from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import connection
from .models import Publication
from django.views.decorators.http import require_http_methods

from django.conf import settings
from utils import *


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
	auth = request.GET.get('auth', '')

	year = request.GET.get('year', '').strip()
	tak = request.GET.get('tak', '').strip()
	author = request.GET.get('author', '').strip()
	filters = request.GET.getlist('countries')

	search_engine = request.GET.get('search-engine', 'off')
	highlight_param = request.GET.get('highlight', 'on')
	highlight_keywords = True if highlight_param == "on" else False



	if search_engine == 'off':
		publications_list = Publication.objects.raw(raw_query(author, filters, year, tak))
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

		'ABSTRACT_WORDS_LIMIT': settings.ABSTRACT_WORDS_LIMIT,
		'highlight_param': highlight_param,
		'highlight_keywords': highlight_keywords,
		'form_f': settings.FORM_F,
		'form_gc': settings.FORM_GC,
		'form_gd': settings.FORM_GD,
		'form_gr': settings.FORM_GR,
		'form_o': settings.FORM_O,
		'form_p1': settings.FORM_P1,
		'form_p2': settings.FORM_P2,
		'form_r': settings.FORM_R,
		'form_te': settings.FORM_TE,
		'form_tt': settings.FORM_TT,

		'auth': settings.AUTH_KEY,
		'q__q': q__q,

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
