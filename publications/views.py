from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import connection
from .models import Publication
from django.views.decorators.http import require_http_methods
from django.contrib.postgres.search import SearchQuery

from django.conf import settings
from utils import formulate_tak_query, query_function, faster_count
import time


def exporting_generator(applied_filters):
    data = Publication.objects.filter(relevance__relevance__gt=10).filter(applied_filters).order_by('year').only("title", "authors", "author100","containername", "publicationtype", "abstract", "year", "doi", "isbn", "location", "daterange", "links", "citation", "identifier", "recordmetadata_zbuamajorversion", "recordmetadata_dateretrieved", "recordmetadata_dateconverted", "recordmetadata_recordtype", "recordmetadata_source", "recordmetadata_recordname", "recordmetadata_searchguid", "recordmetadata_numberinsource", "recordmetadata_zbuaminorversion", "id", "itemdatatype", "itemdatahandler", "created_at", "importedfrom")
    for value in data.iterator(chunk_size=1000):
         yield value.ris_format() + "\n\n"


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
    yearmin = request.GET.get('ymin', '').strip()
    yearmax = request.GET.get('ymax', '').strip()
    tak = request.GET.get('tak', '').strip()
    author = request.GET.get('author', '').strip()
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
    search_engine = request.GET.get('search', 'off')
    search_engine_var = True if search_engine == "off" else False
    highlight = request.GET.get('hlight', 'off')
    highlight_keywords = True if highlight == "off" else False

    if search_engine == 'off':
        myquery = query_function(tak, author, yearmin, yearmax, form_gc_gr, form_gd, form_p1_p2, form_te_tt, form_f, form_o, form_r, below_rank_10)
        if myquery == Q():
            publications_list = Publication.objects.none()
        else:
            publications_list = Publication.objects.select_related('relevance').filter(myquery).order_by('-relevance__relevance').only("id", "title", "authors", "year", "doi", "keywords", "abstract", "relevance", "importedfrom")
    else:
        q_year = q_tak = q_with = Q()
        if yearmin: q_year = Q(year=yearmin)

        if tak: q_tak = formulate_tak_query(tak)

        publications_list = Publication.objects.filter(q_year & (q_tak)).order_by('-year')

    total_records = faster_count()

    per_page = request.GET.get('limit', 50)
    if int(per_page) == 0:
        page_obj = publications_list.all()
        q__q = connection.queries[-1]["sql"]
        total_matched_records = len(publications_list)

    else:
        paginator = Paginator(publications_list, per_page)

        page_obj = paginator.get_page(page_number)

        q__q = connection.queries[-1]["sql"]
        total_matched_records = page_obj.paginator.count

    context = {
        'page_obj': page_obj,
        'total_records': total_records,
        'total_matched_records': total_matched_records,
        'yearmin': yearmin,
        'yearmax': yearmax,
        'tak': tak,
        'author': author,
        'limit': per_page,
        'search_engine_var': search_engine_var,

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
        'timer': str(round(time.time() - start, 2)),

    }
    return render(request, 'publications/index.html', context)

@require_http_methods(["GET"])
@authenticate_user
def showrecord(request):
    auth = request.GET.get('auth', '')

    publication_id = request.GET.get('id')
    publication = Publication.objects.filter(id=publication_id).first()

    highlight = request.GET.get('hlight', 'off')
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
    auth = request.POST.get('auth', '')

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
    form_f = request.POST.getlist('f')
    form_gc_gr = request.POST.getlist('gc/gr')
    form_gd = request.POST.getlist('gd')
    form_o = request.POST.getlist('o')
    form_p1_p2 = request.POST.getlist('p1/p2')
    form_r = request.POST.getlist('r')
    form_te_tt = request.POST.getlist('te/tt')
    rank10 = request.POST.get('rank10', 'off')
    
    zotero_content = exporting_generator(query_function(tak, author, yearmin, yearmax, form_gc_gr, form_gd, form_p1_p2, form_te_tt, form_f, form_o, form_r, False))

    response = StreamingHttpResponse(zotero_content, content_type="application/x-research-info-systems")
    response['Content-Disposition'] = 'attachment; filename="SPUD_RIS_EXPORT.ris"'

    return response

@require_http_methods(["GET"])
@authenticate_user
def keywords(request):
    auth = request.GET.get('auth', '')

    return JsonResponse({'countries': settings.COUNTRIES, 'regions': settings.REGIONS, 'development_terms': settings.DEVELOPMENT_TERMS})

@require_http_methods(["GET"])
@authenticate_user
def detail(request, word):
    auth = request.GET.get('auth', '')
    try:
        keyword_dict = {
    "abkhazia": [
        "Abkhazia",
        "Abkhaz",
        "Abkhazians"
    ],
    "afghanistan": [
        "Afghanistan",
        "Afghan",
        "Afghans"
    ],
    "albania": [
        "Albania",
        "Albanian",
        "Albanians"
    ],
    "algeria": [
        "Algeria",
        "Algerian",
        "Algerians"
    ],
    "andorra": [
        "Andorra",
        "Andorran",
        "Andorrans"
    ],
    "angola": [
        "Angola",
        "Angolan",
        "Angolans"
    ],
    "antiguaandbarbuda": [
        "Antigua and Barbuda",
        "Antiguan and Barbudan",
        "Antiguans and Barbudans",
        "Antigua",
        "Antiguan",
        "Antiguans",
        "Barbuda",
        "Barbudan",
        "Barbudans"
    ],
    "argentina": [
        "Argentina",
        "Argentinian",
        "Argentinians",
        "Argentinean",
        "Argentine"
    ],
    "armenia": [
        "Armenia",
        "Armenian",
        "Armenians"
    ],
    "artsakh": [
        "Artsakh",
        "Artsakhn",
        "Artsakhns",
        "Askeran",
        "Nagorno-Karabakh",
        "Nagorno-Karabakhn",
        "Nagorno-Karabakhns"
    ],
    "australia": [
        "Australia",
        "Australian",
        "Australians",
        "Aussies"
    ],
    "austria": [
        "Austria",
        "Austrian",
        "Austrians"
    ],
    "azerbaijan": [
        "Azerbaijan",
        "Azerbaijani",
        "Azerbaijanis",
        "Azeri"
    ],
    "bahamas": [
        "Bahamas",
        "Bahamian",
        "Bahamians"
    ],
    "bahrain": [
        "Bahrain",
        "Bahraini",
        "Bahrainis"
    ],
    "bangladesh": [
        "Bangladesh",
        "Bengali",
        "Bengalis"
    ],
    "barbados": [
        "Barbados",
        "Bajan",
        "Barbadians"
    ],
    "belarus": [
        "Belarus",
        "Belarusian",
        "Belarusians"
    ],
    "belgium": [
        "Belgium",
        "Belgian",
        "Belgians",
        "Flemish",
        "Flemings"
    ],
    "belize": [
        "Belize",
        "Belizean",
        "Belizeans"
    ],
    "benin": [
        "Benin",
        "Beninese"
    ],
    "bhutan": [
        "Bhutan",
        "Bhutanese"
    ],
    "bolivia": [
        "Bolivia",
        "Bolivian",
        "Bolivians",
        "Plurinational State of Bolivia"
    ],
    "bosniaandherzegovina": [
        "Bosnia and Herzegovina",
        "Bosnia and Herzegovinan",
        "Bosnia and Herzegovinans",
        "Bosnia",
        "Bosnian",
        "Bosnians",
        "Herzegovinan"
    ],
    "botswana": [
        "Botswana",
        "Batswana",
        "Batswanas"
    ],
    "brazil": [
        "Brazil",
        "Brazilian",
        "Brazilians"
    ],
    "bruneidarussalam": [
        "Brunei Darussalam",
        "Brunei",
        "Brunei Darussalamn",
        "Brunei Darussalamns",
        "Bruneian"
    ],
    "bulgaria": [
        "Bulgaria",
        "Bulgarian",
        "Bulgarians"
    ],
    "burkinafaso": [
        "Burkina Faso",
        "Burkinabe",
        "Burkinabes"
    ],
    "burundi": [
        "Burundi",
        "Burundian",
        "Burundians"
    ],
    "cambodia": [
        "Cambodia",
        "Cambodian",
        "Cambodians"
    ],
    "cameroon": [
        "Cameroon",
        "Cameroonian",
        "Cameroonians"
    ],
    "canada": [
        "Canada",
        "Canadian",
        "Canadians"
    ],
    "capeverde": [
        "Cape Verde",
        "Cape Verdean",
        "Cape Verdeans",
        "Cabo Verde",
        "Cabo Verdean",
        "Cabo Verdeans"
    ],
    "catalanrepublic": [
        "Catalan Republic",
        "Catalan",
        "Catalans",
        "Occitans",
        "Catalanes",
        "Catalani"
    ],
    "centralafricanrepublic": [
        "Central African Republic",
        "Central African Republican",
        "Central African Republicans",
        "CAR",
        "Central African"
    ],
    "chad": [
        "Chad",
        "Chadian",
        "Chadians"
    ],
    "chile": [
        "Chile",
        "Chilean",
        "Chileans"
    ],
    "china": [
        "China",
        "Chinese"
    ],
    "colombia": [
        "Colombia",
        "Colombian",
        "Colombians"
    ],
    "comoros": [
        "Comoros",
        "Comorian",
        "Comorians"
    ],
    "congo1democratic": [
        "Democratic Republic of the Congo",
        "Congo, Dem. Rep.",
        "Zaire",
        "Congo-Kinshasa",
        "Zairean",
        "DRC Congolese",
        "DCR",
        "Kinshasa",
        "(Kinshasa) Congolese",
        "Congolese (DRC)",
        "Congo, Democratic Republic of the",
        "Dem. Rep. of the Congo",
        "DRC"
    ],
    "congo2republic": [
        "Republic of the Congo",
        "ROC",
        "ROC Congolese",
        "Brazzaville",
        "Congolese (ROC)",
        "(Brazzaville) Congolese",
        "Congo-Brazzaville",
        "Congo, Rep.",
        "Rep. of the Congo"
    ],
    "congo3z": [
        "Congo",
        "Congolese"
    ],
    "costarica": [
        "Costa Rica",
        "Costa Rican",
        "Costa Ricans"
    ],
    "cotedivoire": [
        "Ivory Coast",
        "Ivorian",
        "Ivorians",
        "C\u00f4te d'Ivoire",
        "C\u00f4te d'Ivoiren",
        "C\u00f4te d'Ivoirens"
    ],
    "croatia": [
        "Croatia",
        "Croatian",
        "Croatians",
        "Croats"
    ],
    "cuba": [
        "Cuba",
        "Cuban",
        "Cubans"
    ],
    "cyprus": [
        "Cyprus",
        "Cypriot",
        "Cypriots"
    ],
    "czechrepublic": [
        "Czech Republic",
        "Czech",
        "Czechs"
    ],
    "denmark": [
        "Denmark",
        "Dane",
        "Danes"
    ],
    "djibouti": [
        "Djibouti",
        "Djiboutians"
    ],
    "dominica2dominica": [
        "Dominican Republic",
        "Dominican Republican",
        "Dominican Republicans",
        "Dominicanos",
        "Domingo"
    ],
    "dominica1nrepublic": [
        "Dominica",
        "Dominican",
        "Dominicans"
    ],
    "easttimor": [
        "Timor-L'este",
        "Timor-L'esten",
        "Timor-L'estens",
        "East Timor",
        "East Timorese",
        "Timor L'este",
        "Timor L'esten",
        "Timor L'estens"
    ],
    "ecuador": [
        "Ecuador",
        "Ecuadorian",
        "Ecuadorians"
    ],
    "egypt": [
        "Egypt",
        "Egyptian",
        "Egyptians"
    ],
    "elsalvador": [
        "El Salvador",
        "Salvadoran",
        "Salvadorans"
    ],
    "eritrea": [
        "Eritrea",
        "Eritrean",
        "Eritreans"
    ],
    "estonia": [
        "Estonia",
        "Estonian",
        "Estonians"
    ],
    "eswatini": [
        "eSwatini",
        "eSwatinin",
        "eSwatinins",
        "Eswatini",
        "Eswatinin",
        "Eswatinins",
        "Kingdom of Eswatini",
        "Swaziland",
        "Swazilander",
        "Swazilanders",
        "weSwatini",
        "weSwatinin",
        "weSwatinins"
    ],
    "ethiopia": [
        "Ethiopia",
        "Ethiopian",
        "Ethiopians"
    ],
    "fiji": [
        "Fiji",
        "Fijian",
        "Fijians"
    ],
    "finland": [
        "Finland",
        "Finish",
        "Finns"
    ],
    "france": [
        "France",
        "French"
    ],
    "gabon": [
        "Gabon",
        "Gabonese"
    ],
    "gambia": [
        "Gambia",
        "Gambian",
        "Gambians",
        "Islamic republic of the Gambia",
        "Republic of the Gambia"
    ],
    "georgia": [
        "Georgia",
        "Georgian",
        "Georgians"
    ],
    "germany": [
        "Germany",
        "German",
        "Germans"
    ],
    "ghana": [
        "Ghana",
        "Ghanaian",
        "Ghanaians"
    ],
    "greece": [
        "Greece",
        "Greek",
        "Greeks",
        "Hellenes"
    ],
    "grenada": [
        "Grenada",
        "Grenadian",
        "Grenadians"
    ],
    "guatemala": [
        "Guatemala",
        "Guatemalan",
        "Guatemalans"
    ],
    "guinea1bissau": [
        "Guinea-Bissau",
        "Guinea-Bissauan",
        "Guinea-Bissauans"
    ],
    "guinea2equatorial": [
        "Equatorial Guinea",
        "Equatorial Guinean",
        "Equatorial Guineans"
    ],
    "guinea3": [
        "Guinea",
        "Guinean",
        "Guineans"
    ],
    "guyana": [
        "Guyana",
        "Guyanese"
    ],
    "haiti": [
        "Haiti",
        "Haitian"
    ],
    "honduras": [
        "Honduras",
        "Honduran",
        "Hondurans"
    ],
    "hungary": [
        "Hungary",
        "Hungarian",
        "Hungarians"
    ],
    "iceland": [
        "Iceland",
        "Icelander",
        "Icelanders",
        "Icelandic"
    ],
    "india": [
        "India",
        "Indian",
        "Indians"
    ],
    "indonesia": [
        "Indonesia",
        "Indonesian",
        "Indonesians"
    ],
    "iran": [
        "Iran",
        "Iranian",
        "Iranians",
        "Iran (Islamic Republic of)"
    ],
    "iraq": [
        "Iraq",
        "Iraqi",
        "Iraqians"
    ],
    "ireland": [
        "Ireland",
        "Irish"
    ],
    "israel": [
        "Israel",
        "Israeli",
        "Israelis"
    ],
    "italy": [
        "Italy",
        "Italian",
        "Italians"
    ],
    "jamaica": [
        "Jamaica",
        "Jamaican",
        "Jamaicans"
    ],
    "japan": [
        "Japan",
        "Japanese"
    ],
    "jordan": [
        "Jordan",
        "Jordanian",
        "Jordanians"
    ],
    "kazakhstan": [
        "Kazakhstan",
        "Kazakhstani",
        "Kazakhstanis"
    ],
    "kenya": [
        "Kenya",
        "Kenyan",
        "Kenyans"
    ],
    "kiribati": [
        "Kiribati",
        "I-Kiribati",
        "I-Kiribatis"
    ],
    "korea1north": [
        "North Korea",
        "Northern Korean",
        "North Koreans",
        "Democratic Republic of Korea"
    ],
    "korean2republic": [
        "Korea",
        "Korean",
        "Koreans"
    ],
    "korea3z": [
        "Korea (Republic of)",
        "Republic of Korea",
        "South Korea",
        "South Koreans",
        "Southern Korea"
    ],
    "kosovo": [
        "Kosovo",
        "Kosovar",
        "Kosovars"
    ],
    "kurdistan": [
        "Kurdistan",
        "Kurdistann",
        "Kurdistanns"
    ],
    "kuwait": [
        "Kuwait",
        "Kuwaiti",
        "Kuwaitis"
    ],
    "kyrgyzstan": [
        "Kyrgyzstan",
        "Kyrgyz",
        "Kyrgyzs"
    ],
    "laos": [
        "Laos",
        "Laotian",
        "Laos People's Democratic Republic"
    ],
    "latvia": [
        "Latvia",
        "Latvian",
        "Latvians"
    ],
    "lebanon": [
        "Lebanon",
        "Lebanese"
    ],
    "lesotho": [
        "Lesotho",
        "Basotho",
        "Basothos"
    ],
    "liberia": [
        "Liberia",
        "Liberian",
        "Liberians"
    ],
    "libya": [
        "Libya",
        "Libyan",
        "Libyans"
    ],
    "liechtenstein": [
        "Liechtenstein",
        "Liechtensteiner",
        "Liechtensteiners"
    ],
    "lithuania": [
        "Lithuania",
        "Lithuanian",
        "Lithuanians"
    ],
    "luxembourg": [
        "Luxembourg",
        "Luxembourger",
        "Luxembourgers"
    ],
    "madagascar": [
        "Madagascar",
        "Malagasy",
        "Malagsys"
    ],
    "malawi": [
        "Malawi",
        "Malawian",
        "Malawians"
    ],
    "malaysia": [
        "Malaysia",
        "Malaysian",
        "Malaysians"
    ],
    "maldives": [
        "Maldives",
        "Maldivan",
        "Maldivans"
    ],
    "mali": [
        "Mali",
        "Malian",
        "Malians"
    ],
    "malta": [
        "Malta",
        "Maltan",
        "Maltans"
    ],
    "marshallislands": [
        "Marshall Islands",
        "Marshallese"
    ],
    "mauritania": [
        "Mauritania",
        "Mauritanian",
        "Mauritanians"
    ],
    "mauritius": [
        "Mauritius",
        "Mauritian",
        "Mauritians",
        "Island of Mauritious"
    ],
    "mexico": [
        "Mexico",
        "Mexican",
        "Mexicans"
    ],
    "micronesia": [
        "Federated States of Micronesia",
        "Micronesia",
        "Micronesian",
        "Micronesians"
    ],
    "moldovan1republicpridnestrovian": [
        "Republic of Moldova",
        "Moldova",
        "Moldovan",
        "Moldovans"
    ],
    "moldova2": [
        "Pridnestrovian Moldovan Republic",
        "Transnistria",
        "Transnistrian",
        "Transnistrians"
    ],
    "monaco": [
        "Monaco",
        "Monacan",
        "Monacans"
    ],
    "mongolia": [
        "Mongolia",
        "Mongolian",
        "Mongolians"
    ],
    "montenegro": [
        "Montenegro",
        "Montenegrin",
        "Montenegrins"
    ],
    "morocco": [
        "Morocco",
        "Moroccan",
        "Moroccans"
    ],
    "mozambique": [
        "Mozambique",
        "Mozambican"
    ],
    "myanmar": [
        "Myanmar",
        "Myanmarn",
        "Myanmarns",
        "Burma",
        "Burman",
        "Burmans",
        "Burmese"
    ],
    "namibia": [
        "Namibia",
        "Namibian",
        "Namibians"
    ],
    "nauru": [
        "Nauru",
        "Naurun",
        "Nauruns",
        "Island of Nauru"
    ],
    "nepal": [
        "Nepal",
        "Nepalese"
    ],
    "netherlands": [
        "Netherlands",
        "Dutch",
        "Holland"
    ],
    "newzealand": [
        "New Zealand",
        "New Zealander",
        "New Zealanders",
        "Kiwi",
        "Kiwis",
        "Aotearoa",
        "Aotearoan",
        "Aotearoans"
    ],
    "nicaragua": [
        "Nicaragua",
        "Nicaraguan",
        "Nicaraguans"
    ],
    "niger": [
        "Niger",
        "Nigerien"
    ],
    "nigeria": [
        "Nigeria",
        "Nigerian",
        "Nigerians"
    ],
    "northcyprus": [
        "North Cyprus",
        "Northern Cypriot",
        "Kuzey Kibris"
    ],
    "northmacedonia": [
        "North Macedonia",
        "Northern Macedonian",
        "North Macedonians",
        "Rep. of Macedonia",
        "Macedonia",
        "Macedonian",
        "Republic of North Macedonia",
        "The former Yugoslav Republic of Macedonia"
    ],
    "norway": [
        "Norway",
        "Norwegian",
        "Norwegians"
    ],
    "oman": [
        "Oman",
        "Omani",
        "Omanis"
    ],
    "pakistan": [
        "Pakistan",
        "Pakistani",
        "Pakistanis"
    ],
    "palau": [
        "Palau",
        "Palauan",
        "Palauns"
    ],
    "palestine": [
        "State of Palestine",
        "Palestine",
        "Palestinian",
        "Palestinians",
        "Palestine, State of"
    ],
    "panama": [
        "Panama",
        "Panamanian",
        "Panamanians"
    ],
    "papuanewguinea": [
        "Papua New Guinea",
        "Papua New Guinean",
        "Papua New Guineans"
    ],
    "paraguay": [
        "Paraguay",
        "Paraguayan",
        "Paraguayans"
    ],
    "peru": [
        "Peru",
        "Peruvian",
        "Peruvians"
    ],
    "philippines": [
        "Philippines",
        "Filipino",
        "Filipinos"
    ],
    "poland": [
        "Poland",
        "Polish",
        "Poles",
        "Pole"
    ],
    "portugal": [
        "Portugal",
        "Portuguese",
        "Portugalns"
    ],
    "puntland": [
        "Puntland",
        "Puntlandn",
        "Puntlandns"
    ],
    "qatar": [
        "Qatar",
        "Qatari",
        "Qataris"
    ],
    "romania": [
        "Romania",
        "Romanian",
        "Romanians"
    ],
    "russia": [
        "Russian Federation",
        "Russian Federations",
        "Russia",
        "Russian",
        "Russians"
    ],
    "rwanda": [
        "Rwanda",
        "Rwandan",
        "Rwandans"
    ],
    "sahrawiarabdemocraticrepublic": [
        "Sahrawi Arab Democratic Republic",
        "Sahrawi Arab Democratic Republicn",
        "Sahrawi Arab Democratic Republicns",
        "Sahrawi Republic",
        "Sahrawi Republican",
        "Sahrawi Republicans",
        "Western Sahara",
        "Western Saharan",
        "Western Saharans"
    ],
    "saintkittsandnevis": [
        "Saint Kitts and Nevis",
        "Saint Kitts and Nevian",
        "Saint Kitts and Nevians",
        "St. Kitts",
        "Nevis"
    ],
    "saintlucia": [
        "Saint Lucia",
        "Saint Lucian",
        "Saint Lucians",
        "St. Lucia"
    ],
    "saintvincentandthegrenadines": [
        "Saint Vincent and the Grenadines",
        "Vincentian",
        "Saint Vincent and the Grenadinesns",
        "St. Vincent",
        "Grenadines"
    ],
    "samoa": [
        "Samoa",
        "Samoan",
        "Samoans"
    ],
    "sanmarino": [
        "San Marino",
        "San Marinon",
        "San Marinons"
    ],
    "saotomeandprincipe": [
        "S\u00e3o Tom\u00e9 and Pr\u00edncipe",
        "S\u00e3o Tom\u00e9 and Pr\u00edncipen",
        "S\u00e3o Tom\u00e9 and Pr\u00edncipens",
        "Sao Tome and Principe",
        "Sao Tome and Principen",
        "Sao Tome and Principens",
        "Sao Tome"
    ],
    "saudiarabia": [
        "Saudi Arabia",
        "Saudi Arabian",
        "Saudi Arabians"
    ],
    "senegal": [
        "Senegal",
        "Senegalese"
    ],
    "serbia": [
        "Serbia",
        "Serbian",
        "Serbians",
        "Serbs"
    ],
    "seychelles": [
        "Seychelles",
        "Seychellois"
    ],
    "sierraleone": [
        "Sierra Leone",
        "Sierra Leonen",
        "Sierra Leonens"
    ],
    "singapore": [
        "Singapore",
        "Singaporean",
        "Singaporeans"
    ],
    "slovakia": [
        "Slovakia",
        "Slovakian",
        "Slovakians",
        "Slovaks"
    ],
    "slovenia": [
        "Slovenia",
        "Slovenian",
        "Slovenians"
    ],
    "solomonislands": [
        "Solomon Islands",
        "Solomon Islander",
        "Solomon Islanders"
    ],
    "somalia": [
        "Somalia",
        "Somalian",
        "Somalians"
    ],
    "somaliland": [
        "Somaliland",
        "Somalilandn",
        "Somalilandns"
    ],
    "southafrica": [
        "South Africa",
        "South African",
        "South Africans",
        "Republic of South Africa",
        "Republic of South African",
        "Republic of South Africans",
        "RSA"
    ],
    "southkorea": [
        "South Korea",
        "South Korean",
        "South Koreans"
    ],
    "southossetia": [
        "South Ossetia",
        "South Ossetian",
        "South Ossetians",
        "the State of Alania",
        "Alania",
        "the State of Alanian",
        "the State of Alanians"
    ],
    "southsudan": [
        "South Sudan",
        "South Sudanese"
    ],
    "spain": [
        "Spain",
        "Spanish",
        "Spaniard",
        "Spaniards",
        "Castillians"
    ],
    "srilanka": [
        "Sri Lanka",
        "Sri Lankan",
        "Sri Lankans"
    ],
    "sudan": [
        "Sudan",
        "Sudanese",
        "Sudanns"
    ],
    "suriname": [
        "Suriname",
        "Surinamer",
        "Surinamers"
    ],
    "sweden": [
        "Sweden",
        "Swedish",
        "Swedes"
    ],
    "switzerland": [
        "Switzerland",
        "Swiss",
        "Suisses",
        "Suisse"
    ],
    "syria": [
        "Syrian Arab Republic",
        "Syrian Arab Republican",
        "Syrian Arab Republicans",
        "Syria",
        "Syrian",
        "Syrians"
    ],
    "tajikistan": [
        "Tajikistan",
        "Tajik",
        "Tajiks"
    ],
    "tanzania": [
        "United Republic of Tanzania",
        "Tanzania",
        "Tanzanian",
        "Tanzanians",
        "Zanzibar"
    ],
    "thailand": [
        "Thailand",
        "Thai"
    ],
    "tibet": [
        "Tibet",
        "Tibetan",
        "Tibetans"
    ],
    "togo": [
        "Togo",
        "Togolese"
    ],
    "tonga": [
        "Tonga",
        "Tongan",
        "Tongans"
    ],
    "trinidadandtobago": [
        "Trinidad and Tobago",
        "Trinidadian",
        "Trinidadians",
        "Trinidad",
        "Tobago"
    ],
    "tunisia": [
        "Tunisia",
        "Tunisian",
        "Tunisians"
    ],
    "turkey": [
        "Turkey",
        "Turkish",
        "Turk",
        "Turks"
    ],
    "turkmenistan": [
        "Turkmenistan",
        "Turkmen",
        "Turkmens"
    ],
    "tuvalu": [
        "Tuvalu",
        "Tuvaluan",
        "Tuvaluns"
    ],
    "uganda": [
        "Uganda",
        "Ugandan",
        "Ugandans"
    ],
    "ukraine": [
        "Ukraine",
        "Ukrainian",
        "Ukrainians"
    ],
    "unitedarabemirates": [
        "United Arab Emirates",
        "Emirian",
        "Emirians",
        "UAE"
    ],
    "unitedkingdom": [
        "United Kingdom",
        "British",
        "Brits",
        "Great Britain",
        "Northern Ireland"
    ],
    "unitedstates": [
        "United States",
        "American"
    ],
    "uruguay": [
        "Uruguay",
        "Uruguayan",
        "Uruguayans"
    ],
    "uzbekistan": [
        "Uzbekistan",
        "Uzbekistani",
        "uzbeks",
        "Uzbeks"
    ],
    "vanuatu": [
        "Vanuatu",
        "Ni-Vanuatu",
        "Ni-Vanuatus",
        "Vanuatus"
    ],
    "vaticancity": [
        "Holy See",
        "Vanticanien",
        "Vanticaniens",
        "Vatican",
        "Vatican City"
    ],
    "venezuela": [
        "Venezuela",
        "Venezuelan",
        "Venezuelans",
        "Bolivarian Republic of Venezuela",
        "Bolivarian Republic of Venezuelan",
        "Bolivarian Republic of Venezuelans"
    ],
    "vietnam2": [
        "Viet Nam",
        "Viet Nams",
        "Viet Namn"
    ],
    "vietnam1": [
        "Vietnam",
        "Vietnamese",
        "Kinh"
    ],
    "yemen": [
        "Yemen",
        "Yemeni"
    ],
    "zambia": [
        "Zambia",
        "Zambian",
        "Zambians"
    ],
    "zimbabwe": [
        "Zimbabwe",
        "Zimbabwean",
        "Zimbabweans"
    ],
    "africa": [
        "Africa",
        "AFR"
    ],
    "arab_world": [
        "Arab world"
    ],
    "asia_pacific": [
        "Asia-Pacific"
    ],
    "caribbean": [
        "Caribbean"
    ],
    "central_africa": [
        "Central Africa"
    ],
    "central_america": [
        "Central America"
    ],
    "central_asia": [
        "Central Asia"
    ],
    "east_africa": [
        "East Africa"
    ],
    "east_africa_community": [
        "East Africa Community",
        "EAC"
    ],
    "east_asia": [
        "East Asia"
    ],
    "east_asia_and_pacific": [
        "East Asia and Pacific",
        "EAP"
    ],
    "eastern_africa": [
        "Eastern Africa"
    ],
    "eastern_asia": [
        "Eastern Asia"
    ],
    "europe_and_central_asia": [
        "Europe and Central Asia",
        "ECA"
    ],
    "horn_of_africa": [
        "Horn of Africa"
    ],
    "latin_america": [
        "Latin America"
    ],
    "latin_america_and_caribbean": [
        "Latin America and Caribbean",
        "LAC"
    ],
    "???": [
        "SRI"
    ],
    "middle_africa": [
        "Middle Africa"
    ],
    "middle_east": [
        "Middle East"
    ],
    "middle_east_and_north_africa": [
        "Middle East and North Africa",
        "MENA"
    ],
    "north_africa": [
        "North Africa"
    ],
    "northern_africa": [
        "Northern Africa"
    ],
    "pacific": [
        "Pacific"
    ],
    "polynesia": [
        "Polynesia"
    ],
    "small_island_development_states": [
        "Small Island Development States",
        "SIDS"
    ],
    "southern_african_development_community": [
        "Southern African Development Community",
        "SADC"
    ],
    "south_america": [
        "South America"
    ],
    "south_asia": [
        "South Asia"
    ],
    "south_asia_region": [
        "South Asia Region",
        "SAR"
    ],
    "southeast_asia": [
        "Southeast Asia"
    ],
    "southeastern_asia": [
        "Southeastern Asia"
    ],
    "southern_africa": [
        "Southern Africa"
    ],
    "southern_asia": [
        "Southern Asia"
    ],
    "sub_saharan_africa": [
        "SSA",
        "Sub-Saharan Africa"
    ],
    "west_africa": [
        "West Africa"
    ],
    "western_africa": [
        "Western Africa"
    ],
    "western_asia": [
        "Western Asia"
    ],
    "conflict_affected_areas": [
        "conflict affected areas",
        "conflict-affected areas"
    ],
    "conflict_affected_regions": [
        "conflict affected regions",
        "conflict-affected regions",
        "conflict zones"
    ],
    "developing_context": [
        "developing context"
    ],
    "developing_countries": [
        "developing countries"
    ],
    "developing_country": [
        "developing country"
    ],
    "developing_economy": [
        "developing economies",
        "developing economy"
    ],
    "developing_market_countries": [
        "developing market countries",
        "developing market country"
    ],
    "developing_markets": [
        "developing markets"
    ],
    "developing_nation": [
        "developing nation"
    ],
    "developing_region": [
        "developing region"
    ],
    "developing_state": [
        "developing state"
    ],
    "developing_world": [
        "developing world"
    ],
    "emergent_nation": [
        "emergent nation",
        "emergent nations"
    ],
    "emerging_economies": [
        "emerging economies"
    ],
    "emerging_market_countries": [
        "emerging market countries",
        "emerging market country"
    ],
    "emerging_nation": [
        "emerging nation"
    ],
    "emerging_world": [
        "emerging world"
    ],
    "fragile_and_conflict_affected_areas": [
        "fragile and conflict affected areas"
    ],
    "fragile_and_conflict_affected_regions": [
        "fragile and conflict affected regions"
    ],
    "fragile_areas": [
        "fragile areas"
    ],
    "fragile_contexts": [
        "fragile contexts"
    ],
    "fragile_regions": [
        "fragile regions"
    ],
    "global_south": [
        "Global South",
        "global south"
    ],
    "growing_economies": [
        "growing economies"
    ],
    "less_developed_countries": [
        "less developed countries",
        "less developed country"
    ],
    "lmic": [
        "LMIC",
        "LMICs",
        "low and middle income countries"
    ],
    "low_income_countries1": [
        "low income countries",
        "low income country"
    ],
    "low_income_environment1": [
        "low income environment"
    ],
    "low_resource_countries1": [
        "low resource countries",
        "low resource country"
    ],
    "low_resource_environment1": [
        "low resource environment"
    ],
    "low_income_countries2": [
        "low-income countries",
        "low-income country"
    ],
    "low_income_environment2": [
        "low-income environment"
    ],
    "low_resource_countries2": [
        "low-resource countries",
        "low-resource country"
    ],
    "low_resource_environment2": [
        "low-resource environment"
    ],
    "middle_income_country": [
        "middle-income country"
    ],
    "middle_income_environment": [
        "middle-income environment",
        "middle income environment"
    ],
    "third_world": [
        "third world",
        "third-world"
    ],
    "under_developed_countries": [
        "under developed countries",
        "under developed country",
        "under-developed countries",
        "under-developed country",
        "underdeveloped countries",
        "underdeveloped country"
    ],
    "under_developed_nation": [
        "under-developed nation",
        "under developed nation",
        "underdeveloped nation"
    ],
    "electronic_whiteboard": [
        "electronic whiteboard"
    ],
    "interactive_whiteboard": [
        "interactive whiteboard"
    ],
    "smart_board": [
        "smart board"
    ],
    "smartboard": [
        "smartboard"
    ],
    "electronic_textbook": [
        "e textbook",
        "e-textbook",
        "electronic textbook",
        "etextbook"
    ],
    "etutor": [
        "e-tutor",
        "Etutor"
    ],
    "free_digital_resources": [
        "FDR",
        "free digital resources"
    ],
    "intelligent_agent": [
        "Intelligent agent"
    ],
    "intelligent_tutoring_system": [
        "Intelligent tutoring system"
    ],
    "learning_platform": [
        "Learning platform"
    ],
    "massive_open_online_course": [
        "MOOC",
        "MOOCs",
        "massive open online course"
    ],
    "moodle": [
        "moodle"
    ],
    "open_educational_resources": [
        "OER",
        "open educational resources"
    ],
    "online_textbook": [
        "online textbook"
    ],
    "online_tutor": [
        "Online tutor"
    ],
    "reusable_learning_object": [
        "Reusable learning object",
        "RLO"
    ],
    "school_website": [
        "School website"
    ],
    "edtech": [
        "EdTech",
        "Education Technology",
        "Educational Technology",
        "edtech"
    ],
    "educational_innovation": [
        "educational innovation"
    ],
    "educational_technologies": [
        "Educational technologies"
    ],
    "emerging_education_technologies": [
        "Emerging education technologies"
    ],
    "emerging_education_technology": [
        "Emerging education technology"
    ],
    "ict_in_classrooms": [
        "ICT in classrooms"
    ],
    "ict_in_the_classroom": [
        "ICT in the classroom"
    ],
    "technology_at_school": [
        "technology at school"
    ],
    "technology_in_education": [
        "technology in education"
    ],
    "technology_in_school": [
        "technology in school"
    ],
    "technology_use_in_education": [
        "technology use in education"
    ],
    "adaptive_learning": [
        "adaptive learning"
    ],
    "asynchronous_learning": [
        "asynchronous learning"
    ],
    "blended_learning": [
        "blended learning"
    ],
    "computer_assisted_instruction1": [
        "CAI"
    ],
    "computer_assisted_instruction2": [
        "computer assisted instruction",
        "computer-assisted instruction"
    ],
    "computer_assisted_learning": [
        "CAL",
        "computer assisted learning"
    ],
    "computer_based_assessment": [
        "computer based assessment"
    ],
    "computer_based_instruction": [
        "computer based instruction",
        "computer-based instruction"
    ],
    "computer_managed_instruction": [
        "computer managed instruction"
    ],
    "computer_mediated_learning": [
        "computer mediated learning",
        "computer-mediated learning"
    ],
    "computer_supported_collaborative_learning": [
        "computer supported collaborative learning"
    ],
    "computer_supported_education": [
        "computer supported education",
        "computer-supported education"
    ],
    "computer_assisted_instructional_programme": [
        "computer-assisted instructional programme"
    ],
    "computerised_learning": [
        "computerised learning",
        "computerized learning"
    ],
    "connected_learning": [
        "connected learning"
    ],
    "differentiated_learning": [
        "differentiated learning"
    ],
    "digital_learning": [
        "digital learning",
        "digital-learning"
    ],
    "distance_education": [
        "distance education"
    ],
    "distance_learning": [
        "distance learning"
    ],
    "distance_learning_program": [
        "distance learning program"
    ],
    "distributed_learning": [
        "distributed learning"
    ],
    "e_learning": [
        "e-learning",
        "elearning",
        "electronic learning"
    ],
    "electronic_classroom": [
        "electronic classroom"
    ],
    "flipped_classroom": [
        "flipped classroom"
    ],
    "flipped_learning": [
        "flipped learning"
    ],
    "free_digital_learning": [
        "FDL",
        "free digital learning"
    ],
    "gamification": [
        "gamification"
    ],
    "hybrid_learning": [
        "H-learning",
        "hybrid learning"
    ],
    "individualised_learning": [
        "individualised learning"
    ],
    "instructional_innovation": [
        "instructional innovation"
    ],
    "instructional_technology": [
        "instructional technology"
    ],
    "integrated_learning_systems": [
        "integrated learning systems"
    ],
    "interactive_learning_environment": [
        "interactive learning environment"
    ],
    "learning": [
        "ubiquitous learning"
    ],
    "media_literacy": [
        "media literacy"
    ],
    "microlearning": [
        "micro learning",
        "micro-learning",
        "microlearning"
    ],
    "mobile_education": [
        "m education",
        "m-education",
        "meducation",
        "mobile education"
    ],
    "mobile_learning": [
        "m learning",
        "m-learning",
        "mlearning",
        "Mobile learning"
    ],
    "multimedia_instruction": [
        "multimedia instruction"
    ],
    "open_and_distance_elearning": [
        "ODEL",
        "open and distance elearning",
        "open and distance e-learning"
    ],
    "open_and_distance_learning": [
        "ODL",
        "open and distance learning"
    ],
    "online_course": [
        "online course"
    ],
    "online_lab": [
        "online lab"
    ],
    "online_laboratory": [
        "online laboratory"
    ],
    "online_learning": [
        "online learning"
    ],
    "open_education": [
        "open education"
    ],
    "open_learning": [
        "open learning"
    ],
    "personalised_learning": [
        "personalised learning",
        "personalized learning"
    ],
    "personalised_teaching": [
        "personalised teaching"
    ],
    "plasma_based_instruction": [
        "plasma-based instruction"
    ],
    "self_directed_learning": [
        "self-directed learning"
    ],
    "self_paced_learning": [
        "self-paced learning"
    ],
    "synchronous_online_learning": [
        "synchronous online learning"
    ],
    "technological_pedagogical_content": [
        "technological pedagogical content"
    ],
    "technology_assisted_learning1": [
        "technology assisted learning"
    ],
    "technology_engagement_teaching_strategy": [
        "Technology engagement teaching strategy",
        "TETS"
    ],
    "technology_enhanced_learning": [
        "Technology enhanced learning",
        "Technology-enhanced learning",
        "TEL"
    ],
    "technology_integration": [
        "technology integration"
    ],
    "technology_assisted_learning2": [
        "technology-assisted learning"
    ],
    "tele_education": [
        "tele education",
        "tele-education",
        "teleeducation"
    ],
    "virtual_classroom": [
        "virtual classroom"
    ],
    "virtual_learning": [
        "virtual learning"
    ],
    "virtual_learning_environment": [
        "virtual learning environment",
        "VLE"
    ],
    "virtual_school": [
        "virtual school"
    ],
    "web_based_instruction": [
        "web based instruction",
        "web-based instruction"
    ],
    "webinar": [
        "webinar"
    ],
    "course_management_system": [
        "CMS",
        "Course Management System"
    ],
    "education_management_information_system": [
        "Education Management Information System",
        "EMIS",
        "education management information system"
    ],
    "examination_systems": [
        "examination systems"
    ],
    "learning_management_systems": [
        "learning management system",
        "LMS"
    ],
    "teacher_development_software": [
        "teacher development software"
    ],
    "textbook_analytics": [
        "textbook analytics"
    ],
    "_3d_printer": [
        "3D printer"
    ],
    "_3d_printing": [
        "3D printing"
    ],
    "access_to_computers": [
        "access to computers"
    ],
    "accessible_technologies": [
        "accessible technologies"
    ],
    "alternative_communication": [
        "alternative communication"
    ],
    "android": [
        "android"
    ],
    "app": [
        "app",
        "application"
    ],
    "apple": [
        "Apple"
    ],
    "assistive_technology": [
        "assistive technology"
    ],
    "audio_recording": [
        "audio recording"
    ],
    "augmentative_communication": [
        "augmentative communication"
    ],
    "bada": [
        "BADA"
    ],
    "bandwidth": [
        "bandwidth"
    ],
    "barriers_to_technology": [
        "barriers to technology"
    ],
    "big_data": [
        "big data"
    ],
    "blackberry": [
        "Blackberry"
    ],
    "blog": [
        "blog"
    ],
    "camera": [
        "camera"
    ],
    "cellphone": [
        "cellphone"
    ],
    "chatbot": [
        "chatbot"
    ],
    "clicker_technology": [
        "clicker technology"
    ],
    "clickers": [
        "clickers"
    ],
    "cloud": [
        "cloud"
    ],
    "cmc": [
        "CMC"
    ],
    "computational_thinking_literacy": [
        "computational thinking literacy"
    ],
    "computer": [
        "computer"
    ],
    "computer_illiteracy": [
        "computer illiteracy"
    ],
    "computer_literacy": [
        "computer literacy"
    ],
    "computer_mediated_communication": [
        "computer-mediated communication"
    ],
    "computerised": [
        "computerised"
    ],
    "computers_on_wheels": [
        "computers on wheels",
        "COWs"
    ],
    "connectivity": [
        "Connectivity"
    ],
    "ct_literacy": [
        "CT literacy"
    ],
    "data": [
        "data"
    ],
    "digital_communication": [
        "digital communication"
    ],
    "digital_content": [
        "digital content"
    ],
    "digital_divide": [
        "digital divide"
    ],
    "digital_exclusion": [
        "digital exclusion"
    ],
    "digital_immigrants": [
        "digital immigrants"
    ],
    "digital_inclusion": [
        "digital inclusion"
    ],
    "digital_literacy": [
        "digital literacy"
    ],
    "digital_native": [
        "Digital native"
    ],
    "digital_resources": [
        "Digital resources"
    ],
    "digital_scrapbook": [
        "Digital scrapbook"
    ],
    "digital_skills": [
        "digital skills"
    ],
    "digital_storytelling": [
        "digital storytelling"
    ],
    "digital_technology": [
        "digital technology",
        "digital technologies"
    ],
    "digital_transformation": [
        "digital transformation"
    ],
    "digitalised": [
        "digitalised"
    ],
    "digitised": [
        "digitised"
    ],
    "discord": [
        "Discord"
    ],
    "disruptive_technology": [
        "disruptive technology"
    ],
    "douban": [
        "Douban"
    ],
    "douyin": [
        "Douyin"
    ],
    "dvd_player": [
        "DVD player"
    ],
    "e_book": [
        "e-book"
    ],
    "e_reader": [
        "e-reader"
    ],
    "earphones": [
        "earphones"
    ],
    "ebook": [
        "Ebook"
    ],
    "ereader": [
        "ereader"
    ],
    "facebook": [
        "Facebook"
    ],
    "gadget": [
        "gadget"
    ],
    "game_console": [
        "game console"
    ],
    "garnet": [
        "Garnet"
    ],
    "geographical_information_systems": [
        "geographical information systems"
    ],
    "hardware": [
        "hardware"
    ],
    "headphones": [
        "headphones"
    ],
    "holograms": [
        "holograms"
    ],
    "i_pad": [
        "i-pad"
    ],
    "ict": [
        "ICT",
        "ICT goods and services",
        "information and communication technology",
        "information and communication technologies"
    ],
    "inclusive_technologies": [
        "inclusive technologies"
    ],
    "influence_of_technology": [
        "influence of technology"
    ],
    "information_communications_technology_literacy": [
        "Information communications technology literacy"
    ],
    "information_literacy": [
        "information literacy"
    ],
    "instagram": [
        "Instagram"
    ],
    "instructional_systems": [
        "instructional systems"
    ],
    "integration_of_technology": [
        "integration of technology"
    ],
    "intel": [
        "intel"
    ],
    "interactive": [
        "interactive"
    ],
    "internet": [
        "Internet",
        "internet"
    ],
    "internet_access": [
        "internet access"
    ],
    "internet_domain": [
        "internet domain"
    ],
    "internet_of_things": [
        "internet of things"
    ],
    "ios": [
        "iOS"
    ],
    "ipad": [
        "iPad",
        "ipad"
    ],
    "iphone": [
        "iphone",
        "iPhone"
    ],
    "information_technology": [
        "I.T.",
        "IT",
        "information technology"
    ],
    "keyboard": [
        "keyboard"
    ],
    "kindle": [
        "kindle"
    ],
    "laptop": [
        "laptop"
    ],
    "linkedin": [
        "LinkedIn"
    ],
    "maemo": [
        "Maemo"
    ],
    "meego": [
        "MeeGo"
    ],
    "metadata": [
        "metadata"
    ],
    "microsoft": [
        "microsoft"
    ],
    "mobile_phone": [
        "mobile phone"
    ],
    "new_media": [
        "new media"
    ],
    "new_technologies": [
        "new technologies"
    ],
    "offline": [
        "offline"
    ],
    "online": [
        "online"
    ],
    "online_discussion": [
        "online discussion"
    ],
    "open_source": [
        "open source"
    ],
    "open_source_software": [
        "open source software"
    ],
    "open_wedos": [
        "Open wedOS"
    ],
    "operating_system": [
        "operating system"
    ],
    "palm_os": [
        "Palm OS"
    ],
    "pinterest": [
        "Pinterest"
    ],
    "platform": [
        "platform"
    ],
    "podcast": [
        "podcast"
    ],
    "poll_everywhere": [
        "Poll Everywhere"
    ],
    "printer": [
        "printer"
    ],
    "qq": [
        "QQ"
    ],
    "qzone": [
        "QZone"
    ],
    "rachel": [
        "RACHEL"
    ],
    "rachel_server": [
        "RACHEL server"
    ],
    "radio": [
        "radio"
    ],
    "raspberry_pi": [
        "Raspberry Pi"
    ],
    "reddit": [
        "Reddit"
    ],
    "sd_card": [
        "SD card"
    ],
    "simulation": [
        "simulation"
    ],
    "sina_weibo": [
        "Sina Weibo"
    ],
    "single_board_computer": [
        "single board computer"
    ],
    "snapchat": [
        "Snapchat"
    ],
    "social_media": [
        "social media"
    ],
    "social_network": [
        "social network"
    ],
    "social_networking_sites": [
        "social networking sites"
    ],
    "software": [
        "software"
    ],
    "supportive_technology": [
        "supportive technology"
    ],
    "symbian": [
        "Symbian"
    ],
    "tablet": [
        "tablet"
    ],
    "technological_literacy": [
        "technological literacy"
    ],
    "technology_leapfrogging": [
        "technology leapfrogging"
    ],
    "technology_enhanced": [
        "technology-enhanced"
    ],
    "telephone": [
        "telephone"
    ],
    "television": [
        "television",
        "TV"
    ],
    "tiktok": [
        "TikTok"
    ],
    "twitter": [
        "Twitter"
    ],
    "verdict": [
        "Verdict"
    ],
    "viber": [
        "Viber"
    ],
    "video_recorder": [
        "video recorder"
    ],
    "videoconferencing": [
        "videoconferencing"
    ],
    "virtual_peer": [
        "virtual peer"
    ],
    "virtual_reality": [
        "VR",
        "Virtual reality"
    ],
    "web": [
        "web"
    ],
    "wechat": [
        "WeChat"
    ],
    "whatsapp": [
        "WhatsApp"
    ],
    "wifi": [
        "WiFi"
    ],
    "wikipedia": [
        "Wikipedia"
    ],
    "windows": [
        "Windows"
    ],
    "youtube": [
        "Youtube"
    ],
    "classroom_assistants": [
        "classroom assistants"
    ],
    "classroom_instruction": [
        "classroom instruction"
    ],
    "district_education_officer": [
        "district education officer"
    ],
    "early_childhood_development": [
        "early childhood development"
    ],
    "early_childhood_education": [
        "early childhood education",
        "ECE"
    ],
    "educators": [
        "educators"
    ],
    "elementary_education": [
        "elementary education"
    ],
    "elementary_school": [
        "elementary school"
    ],
    "faith_school": [
        "faith school"
    ],
    "headteacher": [
        "headteacher"
    ],
    "high_school": [
        "high school"
    ],
    "junior_middle_school": [
        "junior middle school"
    ],
    "junior_school": [
        "junior school"
    ],
    "k_12": [
        "k to 12",
        "k-12"
    ],
    "kindergarten": [
        "kindergarten"
    ],
    "middle_school1": [
        "middle school"
    ],
    "middle_school2": [
        "middle-school"
    ],
    "ministry_of_education": [
        "ministry of education",
        "MoE"
    ],
    "nursery": [
        "nursery"
    ],
    "post_primary1": [
        "post primary"
    ],
    "post_primary2": [
        "post-primary"
    ],
    "pre_primary1": [
        "pre primary"
    ],
    "pre_primary2": [
        "pre-primary"
    ],
    "pre_school": [
        "pre-school"
    ],
    "pre_service_teachers": [
        "pre-service teachers"
    ],
    "primary_education": [
        "primary education"
    ],
    "primary_school": [
        "primary school"
    ],
    "principal": [
        "principal"
    ],
    "private_school": [
        "private school"
    ],
    "refugee_educator": [
        "refugee educator"
    ],
    "school": [
        "school"
    ],
    "school_administrator": [
        "school administrator"
    ],
    "school_authority": [
        "school authority"
    ],
    "school_director": [
        "school director"
    ],
    "school_governing_body": [
        "school governing body"
    ],
    "school_head": [
        "school head"
    ],
    "school_leadership_team": [
        "school leadership team"
    ],
    "school_management_team": [
        "school management team"
    ],
    "school_offical": [
        "school offical"
    ],
    "school_principal": [
        "school principal"
    ],
    "school_supervisor": [
        "school supervisor"
    ],
    "school_teacher": [
        "school teacher"
    ],
    "secondary_education": [
        "secondary education"
    ],
    "secondary_school": [
        "secondary school"
    ],
    "senior_leadership_team": [
        "senior leadership team"
    ],
    "state_school": [
        "state school"
    ],
    "teacher_candidates": [
        "teacher candidates"
    ],
    "teacher_certificate": [
        "teacher certificate"
    ],
    "teacher_cop": [
        "teacher community of practice",
        "teacher communities of practice",
        "teacher COP"
    ],
    "teacher_education": [
        "teacher education"
    ],
    "teacher_professional_development": [
        "teacher professional development",
        "TPD"
    ],
    "teacher_training": [
        "teacher training"
    ],
    "teacher_training_centre": [
        "teacher training centre"
    ],
    "teacher_training_college": [
        "teacher training college"
    ],
    "teacher_training_institute": [
        "teacher training institute"
    ],
    "teachers": [
        "teachers"
    ],
    "teaching_assistant": [
        "teaching assistant"
    ],
    "teaching_assistants": [
        "teaching assistants"
    ],
    "teaching_certificate": [
        "teaching certificate"
    ],
    "accessible_learning": [
        "accessible learning"
    ],
    "alien": [
        "alien"
    ],
    "alienation": [
        "alienation"
    ],
    "asylum": [
        "asylum"
    ],
    "asylum_seeker": [
        "asylum seeker"
    ],
    "at_risk_population": [
        "at-risk population"
    ],
    "bachelors_degree1": [
        "bachelor's degree"
    ],
    "bachelors_degree2": [
        "bachelors degree"
    ],
    "career_entry_support1": [
        "career-entry support"
    ],
    "career_entry_support2": [
        "career entry support"
    ],
    "career_path_training": [
        "career path training"
    ],
    "church": [
        "church"
    ],
    "community_education": [
        "community education"
    ],
    "competency_based_training": [
        "competency-based training"
    ],
    "continuing_education": [
        "continuing education"
    ],
    "continuing_training": [
        "continuing training"
    ],
    "continuous_professional_development": [
        "continuous professional development",
        "CPD"
    ],
    "degree": [
        "degree"
    ],
    "diploma": [
        "diploma"
    ],
    "disabilities": [
        "disabilities"
    ],
    "disability": [
        "disability"
    ],
    "district_level": [
        "district-level"
    ],
    "displaced_person": [
        "displaced person"
    ],
    "displaced_populations": [
        "displaced populations"
    ],
    "education": [
        "education"
    ],
    "education_in_emergencies": [
        "education in emergencies",
        "EiE"
    ],
    "favela": [
        "favela"
    ],
    "fragility_in_education": [
        "fragility in education"
    ],
    "gang_members": [
        "gang members"
    ],
    "geographically_dispersed": [
        "geographically dispersed"
    ],
    "in_service_training": [
        "in-service training"
    ],
    "informal_education": [
        "informal education"
    ],
    "informal_learning": [
        "informal learning"
    ],
    "informal_training": [
        "informal training"
    ],
    "language_learning": [
        "language learning"
    ],
    "learning_community": [
        "learning community"
    ],
    "masters_degree": [
        "master's degree"
    ],
    "masters": [
        "masters"
    ],
    "math": [
        "math"
    ],
    "mathematics": [
        "mathematics"
    ],
    "migrant": [
        "migrant"
    ],
    "minority_ethnic_group": [
        "minority ethnic group"
    ],
    "mosque": [
        "mosque"
    ],
    "moving_populations": [
        "moving populations"
    ],
    "natural_science": [
        "natural science"
    ],
    "non_formal_education": [
        "non-formal education",
        "NFE"
    ],
    "non_formal_learning": [
        "non-formal learning"
    ],
    "postsecondary_education": [
        "postsecondary Education"
    ],
    "pre_service_training": [
        "pre-service training"
    ],
    "professional_continuing_education": [
        "professional continuing education"
    ],
    "professional_education": [
        "professional education"
    ],
    "professional_learning_community": [
        "professional learning community",
        "professional learning communities"
    ],
    "professional_qualification": [
        "professional qualification"
    ],
    "professional_re_education": [
        "professional re-education"
    ],
    "professional_studies": [
        "professional studies"
    ],
    "professional_training": [
        "professional training"
    ],
    "qualification": [
        "qualification"
    ],
    "refugee_education": [
        "refugee education"
    ],
    "refugee_learning": [
        "refugee learning"
    ],
    "science": [
        "science"
    ],
    "science_and_technology": [
        "science and technology"
    ],
    "science_technology_engineering_and_applied_mathematics": [
        "Science Technology Engineering and Applied Mathematics",
        "STEAM"
    ],
    "science_technology_engineering_and_mathematics": [
        "Science Technology Engineering and Mathematics",
        "STEM"
    ],
    "slum": [
        "slum"
    ],
    "special_educational_needs": [
        "special educational needs",
        "SEN"
    ],
    "sen_learner": [
        "SEN learner"
    ],
    "sen_student": [
        "SEN student"
    ],
    "special_educational_needs_and_disabilities": [
        "special educational needs and disabilities",
        "SEND"
    ],
    "special_needs_students": [
        "special needs students"
    ],
    "street_children": [
        "street children"
    ],
    "students": [
        "students"
    ],
    "students_with_disabilities": [
        "students with disabilities"
    ],
    "technical_training": [
        "technical training"
    ],
    "technical_and_vocational_education_and_training": [
        "TVET",
        "Technical and vocational education and training"
    ],
    "vocational_training": [
        "Vocational training"
    ],
    "young_people": [
        "young people"
    ],
    "youth": [
        "youth"
    ],
    "alison": [
        "ALISON"
    ],
    "brck": [
        "BRCK"
    ],
    "bridge": [
        "Bridge"
    ],
    "ck_12": [
        "cK-12"
    ],
    "coursera": [
        "Coursera"
    ],
    "dr_maths": [
        "Dr Maths"
    ],
    "edx": [
        "edX"
    ],
    "egyptian_teachers_first_professional_development_program": [
        "egyptian teachers first professional development program"
    ],
    "ekstep": [
        "EkStep"
    ],
    "emo_haiti": [
        "EMO-Haiti"
    ],
    "eneza": [
        "Eneza"
    ],
    "enlaces": [
        "ENLACES"
    ],
    "enuma": [
        "Enuma"
    ],
    "foundation_for_learning_equality": [
        "Foundation for Learning Equality"
    ],
    "futurelearn": [
        "Futurelearn"
    ],
    "geekie": [
        "Geekie"
    ],
    "hip2bsquared": [
        "Hip2BSquared"
    ],
    "inable": [
        "inABLE"
    ],
    "khan_academy1": [
        "Khan Academy"
    ],
    "khan_academy2": [
        "khan academy"
    ],
    "khanya_project": [
        "KHANYA project"
    ],
    "kolibri": [
        "kolibri"
    ],
    "lego_project": [
        "Lego Project"
    ],
    "mindspark": [
        "Mindspark"
    ],
    "mobilearn": [
        "Mobilearn"
    ],
    "mxit": [
        "Mxit"
    ],
    "nafham": [
        "Nafham"
    ],
    "ole": [
        "OLE"
    ],
    "one_billion": [
        "one billion"
    ],
    "one_laptop_per_child": [
        "One Laptop Per Child"
    ],
    "pratham_books_storyweaver": [
        "Pratham Books\u2019 Storyweaver"
    ],
    "retel": [
        "RETEL Haiti"
    ],
    "rumie": [
        "Rumie"
    ],
    "scratch": [
        "Scratch"
    ],
    "siyavula": [
        "Siyavula"
    ],
    "ted": [
        "TED"
    ],
    "the_connected_learning_initiative": [
        "the connected learning initiative"
    ],
    "the_egyptian_knowledge_bank": [
        "the egyptian knowledge bank"
    ],
    "the_global_digital_library": [
        "The global digital library"
    ],
    "the_queen_rania_teacher_academy": [
        "the queen rania teacher academy"
    ],
    "ubongo": [
        "Ubongo"
    ],
    "udacity": [
        "Udacity"
    ],
    "university_of_the_people": [
        "University of the People"
    ],
    "worldreader": [
        "WorldReader"
    ],
    "xuetangx": [
        "XuetangX"
    ],
    "yoza": [
        "Yoza"
    ],
    "_21st_century_learning": [
        "21st century learning"
    ],
    "academic_achievement": [
        "academic achievement"
    ],
    "access": [
        "access"
    ],
    "access_to_education": [
        "access to education"
    ],
    "accessibility": [
        "accessibility"
    ],
    "accountability": [
        "Accountability"
    ],
    "achievement": [
        "achievement"
    ],
    "achievement_gap": [
        "achievement gap"
    ],
    "aid": [
        "Aid"
    ],
    "assessment": [
        "assessment"
    ],
    "attainment": [
        "attainment"
    ],
    "attendance": [
        "attendance"
    ],
    "attitude": [
        "attitude"
    ],
    "attribution": [
        "attribution"
    ],
    "bank": [
        "Bank"
    ],
    "banking": [
        "Banking"
    ],
    "behavior": [
        "behavior"
    ],
    "behaviour": [
        "behaviour"
    ],
    "budgeting": [
        "budgeting"
    ],
    "change_management": [
        "change management"
    ],
    "charity": [
        "charity"
    ],
    "constraints": [
        "constraints"
    ],
    "constructivism": [
        "constructivism"
    ],
    "constructivist": [
        "constructivist"
    ],
    "consumption_and_capital_investment": [
        "consumption and capital investment"
    ],
    "cost": [
        "cost"
    ],
    "cost_analysis": [
        "cost analysis"
    ],
    "cost_benefit_analysis": [
        "cost benefit analysis"
    ],
    "cost_classification": [
        "cost classification"
    ],
    "cost_effectiveness": [
        "cost effectiveness"
    ],
    "cost_of_living": [
        "cost of living"
    ],
    "curricula": [
        "curricula"
    ],
    "curriculum": [
        "curriculum"
    ],
    "demand": [
        "demand"
    ],
    "decision_making": [
        "decision-making"
    ],
    "dialogic_pedagogy": [
        "dialogic learning",
        "dialogic pedagogy",
        "dialogic teaching"
    ],
    "dialogue": [
        "dialogue"
    ],
    "digital_economy": [
        "digital economy"
    ],
    "digital_goods_and_services": [
        "digital goods and services"
    ],
    "digital_trade": [
        "digital trade"
    ],
    "discriminatory_taxes": [
        "discriminatory taxes"
    ],
    "diversity": [
        "diversity"
    ],
    "divided_societies": [
        "divided societies"
    ],
    "domestic_education_spending": [
        "domestic education spending"
    ],
    "donor": [
        "donor"
    ],
    "donor_sponsored": [
        "donor-sponsored"
    ],
    "early_literacy": [
        "early literacy"
    ],
    "economic_factors": [
        "economic Factors"
    ],
    "economics": [
        "economics"
    ],
    "education_financing": [
        "education financing"
    ],
    "education_rbf": [
        "education RBF"
    ],
    "education_results_based_financing": [
        "education results-based financing"
    ],
    "educational_equality": [
        "educational equality"
    ],
    "educational_equity": [
        "educational equity"
    ],
    "educational_opportunities": [
        "educational opportunities"
    ],
    "efficiency": [
        "efficiency"
    ],
    "emancipation": [
        "emancipation"
    ],
    "empowerment": [
        "empowerment"
    ],
    "equity": [
        "equity"
    ],
    "exclusion": [
        "exclusion"
    ],
    "expenditures": [
        "expenditures"
    ],
    "expense": [
        "expense"
    ],
    "female": [
        "female"
    ],
    "federal_aid": [
        "federal aid"
    ],
    "finance": [
        "finance"
    ],
    "financers": [
        "financers"
    ],
    "financial_feasibility": [
        "financial feasibility"
    ],
    "financial_policy": [
        "financial policy"
    ],
    "financial_stream": [
        "financial stream"
    ],
    "financial_support": [
        "financial support"
    ],
    "financing": [
        "financing"
    ],
    "flexible": [
        "flexible"
    ],
    "fund_raising": [
        "fund raising"
    ],
    "funder": [
        "funder"
    ],
    "funding": [
        "funding"
    ],
    "funding_formula": [
        "funding formula"
    ],
    "funding_proposals": [
        "funding proposals"
    ],
    "fundraising": [
        "fundraising"
    ],
    "gender": [
        "gender"
    ],
    "gender_equality": [
        "gender equality"
    ],
    "girl": [
        "girl"
    ],
    "government": [
        "government"
    ],
    "government_funding": [
        "government funding"
    ],
    "government_role": [
        "government role"
    ],
    "high_tariffs": [
        "high tariffs"
    ],
    "improvement": [
        "improvement"
    ],
    "incentives": [
        "incentives"
    ],
    "incidental_learning": [
        "incidental learning"
    ],
    "inclusion": [
        "inclusion"
    ],
    "inclusive_education": [
        "inclusive education"
    ],
    "inclusive_learning": [
        "inclusive learning"
    ],
    "information_sciences": [
        "information sciences"
    ],
    "instructional_design": [
        "instructional design"
    ],
    "instructionalism": [
        "instructionalism"
    ],
    "interactionism": [
        "interactionism"
    ],
    "interactive_pedagogy": [
        "interactive pedagogy"
    ],
    "interactive_teaching": [
        "interactive teaching"
    ],
    "intercultural": [
        "intercultural"
    ],
    "integration": [
        "integration"
    ],
    "internet_economy": [
        "internet economy"
    ],
    "investments": [
        "Investments"
    ],
    "leadership": [
        "leadership"
    ],
    "learning_ecologies": [
        "learning ecologies"
    ],
    "life_wide_learning": [
        "life-wide learning"
    ],
    "lifelong_learning": [
        "lifelong learning"
    ],
    "limitations": [
        "limitations"
    ],
    "literacy": [
        "literacy"
    ],
    "literacy_assessment": [
        "literacy assessment"
    ],
    "management": [
        "management"
    ],
    "millennium_development_goals": [
        "MDG",
        "millennium development goals"
    ],
    "ministry": [
        "ministry"
    ],
    "monitoring_and_evaluation": [
        "M&E",
        "monitoring and evaluation"
    ],
    "monitoring_evaluation_and_learning": [
        "MEL",
        "monitoring evaluation and learning"
    ],
    "motivation": [
        "motivation"
    ],
    "mulitlingual_education": [
        "mulitlingual education"
    ],
    "neo_colonialism": [
        "neo-colonialism"
    ],
    "neo_liberalism": [
        "neo-liberalism"
    ],
    "neocolonialism": [
        "neocolonialism"
    ],
    "neoliberalism": [
        "neoliberalism"
    ],
    "non_mother_tongue_language_acquisition": [
        "non-mother-tongue language acquisition"
    ],
    "numeracy": [
        "numeracy"
    ],
    "numeracy_assessment": [
        "numeracy assessment"
    ],
    "opportunity_cost": [
        "opportunity cost"
    ],
    "outcomes": [
        "outcomes"
    ],
    "pay": [
        "pay"
    ],
    "payment": [
        "payment"
    ],
    "pedagogy": [
        "pedagogy"
    ],
    "philanthropic_foundations": [
        "philanthropic foundations"
    ],
    "policy": [
        "policy"
    ],
    "private_financial_support": [
        "private financial support"
    ],
    "private_public_partnership": [
        "PPP",
        "Private Public Partnership"
    ],
    "pro_poor": [
        "pro-poor"
    ],
    "problem_based_learning": [
        "PBL",
        "problem-based learning"
    ],
    "profit": [
        "profit"
    ],
    "profitability": [
        "profitability"
    ],
    "public_expenditure_on_education": [
        "public expenditure on education"
    ],
    "public_relations": [
        "public relations"
    ],
    "reading": [
        "reading"
    ],
    "regulation": [
        "regulation"
    ],
    "remuneration": [
        "remuneration"
    ],
    "resource_allocation": [
        "resource Allocation"
    ],
    "returns": [
        "returns"
    ],
    "rewards": [
        "rewards"
    ],
    "rural": [
        "rural"
    ],
    "salary": [
        "salary"
    ],
    "scalabilty": [
        "scalability"
    ],
    "scholarships": [
        "scholarships"
    ],
    "school_management": [
        "school management"
    ],
    "sustainable_development_goals": [
        "SDG",
        "sustainable development goals",
        "sustainable development goal"
    ],
    "service_providers": [
        "service providers"
    ],
    "socio_culturalism": [
        "socio-culturalism"
    ],
    "socioeconomic_status": [
        "socioeconomic Status"
    ],
    "special_needs": [
        "special needs"
    ],
    "standards": [
        "standards"
    ],
    "state_aid": [
        "state aid"
    ],
    "supply": [
        "supply"
    ],
    "sustainability": [
        "sustainability"
    ],
    "sustainable_revenue_streams": [
        "sustainable revenue streams"
    ],
    "systems": [
        "systems"
    ],
    "taxation_regimes": [
        "taxation regimes"
    ],
    "taxes": [
        "taxes"
    ],
    "teacher_absenteeism": [
        "teacher absenteeism"
    ],
    "teacher_attendance": [
        "teacher attendance"
    ],
    "teacher_identity": [
        "teacher identity"
    ],
    "teacher_motivation": [
        "teacher motivation"
    ],
    "teaching_approach": [
        "teaching approach"
    ],
    "teaching_method": [
        "teaching method"
    ],
    "trade_and_investment_system": [
        "trade and investment system"
    ],
    "training_needs": [
        "training needs"
    ],
    "training_pathway": [
        "training pathway"
    ],
    "women": [
        "women"
    ],
    "urban": [
        "urban"
    ],
    "action_research": [
        "action research"
    ],
    "adaptive": [
        "adaptive"
    ],
    "agile": [
        "agile"
    ],
    "anarchy": [
        "anarchy"
    ],
    "case_study": [
        "case study"
    ],
    "citizen_science": [
        "citizen science"
    ],
    "correlation": [
        "correlation"
    ],
    "critical_realism": [
        "critical realism"
    ],
    "critical_theory": [
        "critical theory"
    ],
    "design_based_implementation_research": [
        "DBIR",
        "design-based implementation research"
    ],
    "design_based_research": [
        "DBR",
        "design-based research"
    ],
    "deductive": [
        "deductive"
    ],
    "difference_in_differences": [
        "difference in differences"
    ],
    "engineering_based_research": [
        "EBR",
        "engineering-based research"
    ],
    "evaluation": [
        "evaluation"
    ],
    "experimental_design": [
        "experimental design"
    ],
    "focus_groups": [
        "focus groups"
    ],
    "formative_research": [
        "formative research"
    ],
    "grounded_theory": [
        "grounded theory"
    ],
    "group_discussions": [
        "group discussions"
    ],
    "hermeneutics": [
        "hermeneutics"
    ],
    "historical": [
        "historical"
    ],
    "impact": [
        "impact"
    ],
    "inductive": [
        "inductive"
    ],
    "interview": [
        "interview"
    ],
    "iterative": [
        "iterative"
    ],
    "lean": [
        "lean"
    ],
    "learning_analytics": [
        "learning analytics"
    ],
    "literature_analysis": [
        "literature analysis"
    ],
    "literature_review": [
        "literature review"
    ],
    "long_interview": [
        "long interview"
    ],
    "meta_analysis": [
        "meta-analysis"
    ],
    "mixed_method": [
        "mixed method",
        "mixed methods",
        "mixed-method",
        "mixed-methods",
        "Multiple research approach",
        "Multimethod",
        "multimethodology",
        "combined research",
        "triangulation",
        "triangulate",
        "multi-method",
        "complement",
        "complementarity",
        "mixed analysis",
        "mixed research",
        "hybrid methods",
        "construct research",
        "integrated research"
    ],
    "modelling": [
        "modelling"
    ],
    "observation": [
        "observation"
    ],
    "participatory_video": [
        "participatory video"
    ],
    "positivist": [
        "positivist"
    ],
    "quasi_experimental_design": [
        "QED",
        "quasi-experimental design",
        "field experiment ",
        "randomly sampled",
        "representative sample"
    ],
    "qualitative": [
        "qualitative"
    ],
    "quantitative": [
        "quantitative"
    ],
    "questionnaire": [
        "questionnaire"
    ],
    "randomised_control_trial": [
        "randomised control trial",
        "RCT",
        "randomised control trials",
        "randomized control trial",
        "randomized controlled trial",
        "randomized controlled trials"
    ],
    "regression": [
        "regression"
    ],
    "regression_discontinuity_design": [
        "regression discontinuity design"
    ],
    "research_design": [
        "research design",
        "study design",
        "project design"
    ],
    "research_method": [
        "research method",
        "research methodology",
        "research methods",
        "research approach"
    ],
    "rich_text_analysis": [
        "rich text analysis"
    ],
    "semi_structured_interview": [
        "semi-structured interview"
    ],
    "structured_interview": [
        "structured interview"
    ],
    "survey": [
        "survey"
    ],
    "synthesis": [
        "synthesis"
    ],
    "systematic_review": [
        "systematic review"
    ],
    "tracer_study": [
        "tracer study"
    ],
    "trial": [
        "trial"
    ],
    "unstructured_interview": [
        "unstructured interview"
    ],
    "usability": [
        "usability"
    ],
    "video": [
        "video "
    ],
    "program_evaluation": [
        "program evaluation"
    ],
    "programme_evaluation": [
        "programme evaluation"
    ]
    }
        lexemes = keyword_dict[word]
    except:
        raise Http404("Semantic value does not exist")
    return render(request, 'publications/detail.html', {'semantic_value': word, 'semantic_lexemes': lexemes, 'auth': auth})