from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import connection
from .models import Publication
from django.views.decorators.http import require_http_methods
from django.contrib.postgres.search import SearchQuery

from django.conf import settings
from utils import *
import time



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
    #start = time.time()

    auth = request.GET.get('auth', '')
    yearmin = request.GET.get('ymin', '').strip()
    yearmax = request.GET.get('ymax', '').strip()
    tak = request.GET.get('tak', '').strip()
    author = request.GET.get('author', '').strip()
    min_hdi = request.GET.get('hmin', '').strip()
    max_hdi = request.GET.get('hmax', '').strip()
    form_f = request.GET.getlist('F')
    form_gc_gr = request.GET.getlist('GCGR')
    form_gd = request.GET.getlist('GD')
    form_o = request.GET.getlist('O')
    form_p1_p2 = request.GET.getlist('P1P2')
    form_r = request.GET.getlist('R')
    form_te_tt = request.GET.getlist('TETT')
    page_number = request.GET.get('page')

    rank10 = request.GET.get('rank10', 'off')
    below_rank_10 = True if rank10 == "off" else False
    search_engine = request.GET.get('search-engine', 'off')
    highlight = request.GET.get('highlight', 'off')
    highlight_keywords = True if highlight == "off" else False

    if min_hdi and not max_hdi:
        max_hdi = 1
    elif max_hdi and not min_hdi:
        min_hdi = 0

    if search_engine == 'off':
        myquery = query_function(tak, author, yearmin, yearmax, form_gc_gr, form_gd, form_p1_p2, form_te_tt, form_f, form_o, form_r, below_rank_10, min_hdi, max_hdi)
        if myquery == Q():
            publications_list = Publication.objects.none()
            total_matched_records = 0
        else:
            publications_list = Publication.objects.select_related('relevance').filter(myquery).order_by('-relevance__relevance').only("id", "title", "authors", "year", "doi", "keywords", "abstract", "relevance", "importedfrom")
            total_matched_records = len(publications_list)
    else:
        q_year = q_tak = q_with = Q()
        if year_min: q_year = Q(year=yearmin)

        if tak: q_tak = formulate_tak_query(tak)

        publications_list = Publication.objects.filter(q_year & (q_tak)).order_by('-year')
        paginator = Paginator(publications_list, per_page)

        page_obj = paginator.get_page(page_number)

        q__q = connection.queries[-1]["sql"]

        total_matched_records = page_obj.paginator.count


    total_records = faster_count()

    per_page = request.GET.get('limit', 50)
    if int(per_page) == 0:
        page_obj = publications_list.all()
        q__q = connection.queries[-1]["sql"]

    else:
        paginator = Paginator(publications_list, per_page)

        page_obj = paginator.get_page(page_number)

        q__q = connection.queries[-1]["sql"]

    context = {
        'page_obj': page_obj,
        'total_records': total_records,
        'total_matched_records': total_matched_records,
        'yearmin': yearmin,
        'yearmax': yearmax,
        'tak': tak,
        'author': author,
        'limit': per_page,
        'min_hdi': min_hdi,
        'max_hdi': max_hdi,

        'form_f': form_f,
        'FORM_F': settings.FORM_F,
        'form_gc_gr': form_gc_gr,
        'FORM_GC_GR': settings.FORM_GC_GR,
        'form_gd': form_gd,
        'FORM_GD': settings.FORM_GD,
        'form_o': form_o,
        'FORM_O': settings.FORM_O,
        'form_p1_p2': form_p1_p2,
        'FORM_P1_P2': settings.FORM_P1_P2,
        'form_r': form_r,
        'FORM_R': settings.FORM_R,
        'form_te_tt': form_te_tt,
        'FORM_TE_TT': settings.FORM_TE_TT,

        'ABSTRACT_WORDS_LIMIT': settings.ABSTRACT_WORDS_LIMIT,
        'highlight': highlight,
        'highlight_keywords': highlight_keywords,
        'below_rank_10': below_rank_10,
        'KEYWORDS_LIST': settings.KEYWORDS.items(),

        'auth': settings.AUTH_KEY,
        'q__q': q__q,
        #'timer': str(round(time.time() - start, 2)),

    }
    return render(request, 'publications/index.html', context)

@require_http_methods(["GET"])
@authenticate_user
def showrecord(request):
    auth = request.GET.get('auth', '')

    publication_id = request.GET.get('id')
    publication = Publication.objects.filter(id=publication_id).first()

    highlight = request.GET.get('highlight', 'off')
    highlight_keywords = True if highlight == "off" else False

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
    auth = request.POST.get('auth', '')
    yearmin = request.POST.get('ymin', '').strip()
    yearmax = request.POST.get('ymax', '').strip()
    tak = request.POST.get('tak', '').strip()
    author = request.POST.get('author', '').strip()
    min_hdi = request.POST.get('hmin', '').strip()
    max_hdi = request.POST.get('hmax', '').strip()
    form_f = request.POST.getlist('f')
    form_gc_gr = request.POST.getlist('gc/gr')
    form_gd = request.POST.getlist('gd')
    form_o = request.POST.getlist('o')
    form_p1_p2 = request.POST.getlist('p1/p2')
    form_r = request.POST.getlist('r')
    form_te_tt = request.POST.getlist('te/tt')
    rank10 = request.POST.get('rank10', 'off')
    below_rank_10 = True if rank10 == "off" else False
    
    publications = Publication.objects.select_related('relevance').filter(query_function(tak, author, yearmin, yearmax, form_gc_gr, form_gd, form_p1_p2, form_te_tt, form_f, form_o, form_r, below_rank_10, min_hdi, max_hdi)).order_by('-relevance__relevance').only("id", "title", "authors", "year", "doi", "keywords", "abstract", "relevance", "importedfrom")

    zotero_content = [(publication.ris_format() + "\n\n") for publication in publications]

    response = HttpResponse(zotero_content, content_type="application/x-research-info-systems")
    response['Content-Disposition'] = 'attachment; filename="SPUD_RIS_EXPORT.ris"'

    return response

@require_http_methods(["GET"])
@authenticate_user
def keywords(request):
    auth = request.GET.get('auth', '');

    return JsonResponse({'countries': settings.COUNTRIES, 'regions': settings.REGIONS, 'development_terms': settings.DEVELOPMENT_TERMS})
