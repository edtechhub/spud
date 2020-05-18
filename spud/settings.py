"""
Django settings for spud project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import logging

import environ
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
        },
    },
    'loggers': {
        'mylogger': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}

ALLOWED_HOSTS = ["127.0.0.1", "localhost"].append(env("ALLOWED_HOSTS"))


# Application definition

INSTALLED_APPS = [
    'publications.apps.PublicationsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'spud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'spud.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
if os.getenv('GAE_APPLICATION', None):
    # this is for server settings on google application engine
    SECURE_SSL_REDIRECT = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': env("PRODUCTION_HOST"),
            'NAME': env("PRODUCTION_DATABASE_NAME"),
            'USER': env("PRODUCTION_USER"),
            'PASSWORD': env("PRODUCTION_PASSWORD"),
            'PORT': env("PRODUCTION_PORT"),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': env("STAGING_HOST"),
            'NAME': env("STAGING_DATABASE_NAME"),
            'USER': env("STAGING_USER"),
            'PASSWORD': env("STAGING_PASSWORD"),
            'PORT': env("STAGING_PORT"),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

WITH_FILTERS = {
    "GC.H": {
        "regex": [],
        "iregex": ["\y(Chad|Ghana|India|Kenya|Mali|Nepal|Niger|Peru|Sudan)\y", "(Bangladesh|Burkina Faso|Burundi|Central African Republic|Comoros|Democratic Republic of the Congo|Eritrea|Ethiopia|Gambia|Guinea.Bissau|Jordan|Lebanon|Liberia|Malawi|Mozambique|Nigeria|Pakistan|Philippines|Rwanda|Sierra Leone|South Sudan|United Republic of Tanzania|Uganda|Zambia|Zimbabwe)"],
    },

    "GC.H or GC.M": {
        "regex": ["\y(DRC|RSA)\y"],
        "iregex": ["\y(Niger|Nigeran)\y", "(Chad|Ghana|India|Kenya|Mali|Nepal|Niger|Peru|Sudan|Benin|China|Congo|Cuba|Egypt|Fiji|Gabon|Haiti|Iraq|Iraq|Laos|Libya|Burma|Nauru|Nauru|Syria|Tibet|Togo|Yemen|Bangladesh|Burkina Faso|Burundi|Central African Republic|Comoros|Democratic Republic of the Congo|Eritrea|Ethiopia|Gambia|Guinea.Bissau|Jordan|Lebanon|Liberia|Malawi|Mozambique|Nigeria|Pakistan|Philippines|Rwanda|Sierra Leone|South Sudan|United Republic of Tanzania|Uganda|Zambia|Zimbabwe|Abkhazia|Afghanistan|Algeria|Angola|Armenia|Artsakh|Nagorno.Karabakh|Azerbaijan|Belize|Bhutan|Bolivia|Plurinational State of Bolivia|Bosnia and Herzegovina|Botswana|Brazil|Cambodia|Cameroon|Cabo Verde|Cape Verde|Central African Republic|Colombia|Republic of the Congo|Costa Rica|Côte d.Ivoire|Ivory Coast|Congo|Djibouti|Dominican Republic|East Timor|Timor L.este|Timor.L.este|Ecuador|El Salvador|El Salvador|Equatorial Guinea|eSwatini|Eswatini|Kingdom of Eswatini|Swaziland|Swaziland|Gambia|Guatemala|Guinea|Guinea|Guyana|Honduras|Indonesia|Jamaica|Kiribati|Kurdistan|Kyrgyzstan|Kyrgyzstan|Kyrgyzstan|Laos People.s Democratic Republic|Lesotho|Liberia|Madagascar|Maldives|Maldives|Mauritania|Mauritius|Mauritius|Mexico|Federated States of Micronesia|Micronesia|Moldova|Republic of Moldova|Mongolia|Morocco|Myanmar|Namibia|Nicaragua|North Korea|North Macedonia|Macedonia|Republic of North Macedonia|The former Yugoslav Republic of Macedonia|Palestine|Palestine, State of|State of Palestine|Panama|Papua New Guinea|Paraguay|Pridnestrovian Moldovan Republic|Transnistria|Puntland|Romania|Russia|Russian Federation|Sahrawi Arab Democratic Republic|Sahrawi Republic|Western Sahara|Saint Lucia|Sao Tome and Principe|São Tomé and Príncipe|Senegal|Serbia|Solomon Islands|Somalia|Somaliland|Republic of South Africa|South Africa|South Ossetia|the State of Alania|Sri Lanka|Suriname|Suriname|Syrian Arab Republic|Tajikistan|Tanzania|Thailand|Tunisia|Turkey|Turkmenistan|Tuvalu|Ukraine|Uzbekistan|Vanuatu|Bolivarian Republic of Venezuela|Venezuela|Viet Nam|Vietnam)"],
    },

    "GC.HM or GR or GD": {
        "regex": ["\y(DRC|RSA|AFR|EAC|EAP|ECA|LAC|MENA|SIDS|SADC|SAR|SSA|LMIC)\y"],
        "iregex": ["\y(Chad|Ghana|India|Kenya|Mali|Nepal|Niger|Peru|Sudan|Benin|China|Congo|Cuba|Egypt|Fiji|Gabon|Haiti|Iraq|Iraq|Laos|Libya|Burma|Nauru|Nauru|Syria|Tibet|Togo|Yemen|LMICs)\y", "(Bangladesh|Burkina Faso|Burundi|Central African Republic|Comoros|Democratic Republic of the Congo|Eritrea|Ethiopia|Gambia|Guinea.Bissau|Jordan|Lebanon|Liberia|Malawi|Mozambique|Nigeria|Pakistan|Philippines|Rwanda|Sierra Leone|South Sudan|United Republic of Tanzania|Uganda|Zambia|Zimbabwe|Abkhazia|Afghanistan|Algeria|Angola|Armenia|Artsakh|Nagorno.Karabakh|Azerbaijan|Belize|Bhutan|Bolivia|Plurinational State of Bolivia|Bosnia and Herzegovina|Botswana|Brazil|Cambodia|Cameroon|Cabo Verde|Cape Verde|Central African Republic|Colombia|Congo, Rep.|Congo, Rep.|Rep. of the Congo|Republic of the Congo|Republic of the Congo|Costa Rica|Côte d.Ivoire|Ivory Coast|Congo, Dem. Rep.|Congo, Democratic Republic of the|Dem. Rep. of the Congo|Democratic Republic of the Congo|Djibouti|Dominican Republic|East Timor|Timor L.este|Timor.L.este|Ecuador|El Salvador|El Salvador|Equatorial Guinea|eSwatini|Eswatini|Kingdom of Eswatini|Swaziland|Swaziland|Islamic republic of the Gambia|Republic of the Gambia|Georgia|Guatemala|Guinea|Guinea|Guyana|Honduras|Indonesia|Jamaica|Kiribati|Kurdistan|Kyrgyzstan|Kyrgyzstan|Kyrgyzstan|Laos People.s Democratic Republic|Lesotho|Liberia|Madagascar|Maldives|Maldives|Mauritania|Mauritius|Mauritius|Mexico|Federated States of Micronesia|Micronesia|Moldova|Republic of Moldova|Mongolia|Morocco|Myanmar|Namibia|Nicaragua|North Korea|North Macedonia|Rep. of Macedonia|Republic of North Macedonia|The former Yugoslav Republic of Macedonia|Palestine|Palestine, State of|State of Palestine|Panama|Papua New Guinea|Paraguay|Pridnestrovian Moldovan Republic|Transnistria|Puntland|Romania|Russia|Russian Federation|Sahrawi Arab Democratic Republic|Sahrawi Republic|Western Sahara|Saint Lucia|Sao Tome and Principe|São Tomé and Príncipe|Senegal|Serbia|Solomon Islands|Somalia|Somaliland|Republic of South Africa|South Africa|South Ossetia|the State of Alania|Sri Lanka|Suriname|Suriname|Syrian Arab Republic|Tajikistan|Tanzania|Thailand|Tunisia|Turkey|Turkmenistan|Tuvalu|Ukraine|Uzbekistan|Vanuatu|Bolivarian Republic of Venezuela|Venezuela|Viet Nam|Vietnam|Africa|Arab world|Asia.Pacific|Caribbean|Central Africa|Central America|Central Asia|East Africa|East Africa Community|East Asia|East Asia and Pacific|Eastern Africa|Eastern Asia|Europe and Central Asia|Horn of Africa|Latin America|Latin America and Caribbean|Micronesia|Middle Africa|Middle East|Middle East and North Africa|North Africa|Northern Africa|Pacific|Polynesia|Small Island Development States|Southern African Development Community|South America|South Asia|South Asia Region|Southeast Asia|Southeastern Asia|Southern Africa|Southern Asia|Sub.Saharan Africa|West Africa|Western Africa|Western Asia|conflict affected areas|conflict.affected areas|conflict affected regions|conflict.affected regions|conflict zones|developing context|developing countries|developing country|developing economies|developing economy|developing market countries|developing market country|developing markets|developing nation|developing region|developing state|developing world|emergent nation|emergent nations|emerging economies|emerging market countries|emerging market country|emerging nation|emerging world|fragile and conflict affected areas|fragile and conflict affected regions|fragile areas|fragile contexts|fragile regions|Global South|growing economies|less developed countries|less developed country|low and middle income countries|low income countries|low income country|low income environment|low resource countries|low resource country|low resource environment|low.income countries|low.income country|low.income environment|low.resource countries|low.resource country|low.resource environment|middle.income country|middle.income country|middle.income country|middle.income environment|middle income environment|third world|third.world|under developed countries|under developed country|under.developed countries|under.developed country|underdeveloped countries|underdeveloped country|under.developed nation|under developed nation|underdeveloped nation)"],
    },

    "PP": {
        "regex": ["\y(ECE|TPD|CPD|NFE|SEN|SEND|STEAM|STEM|TVET)\y", "(MoE|EiE)"],
        "iregex": ["(k-12|alien|math|slum|youth|district education officer|early childhood education|elementary school|headteacher|high school|junior middle school|junior school|k to 12|kindergarten|lower secondary|middle school|middle.school|ministry of education|nursery|post primary|post.primary|pre primary|pre.primary|pre.school|pre.service teachers|primary education|primary school|principal|school|school governing body|school head|school leadership team|school management team|school offical|school principal|school teacher|secondary education|secondary school|senior leadership team|teacher candidates|teacher certificate|teacher community of practice|teacher communities of practice|teacher COP|teacher education|teacher professional development|teacher training|teacher training centre|teacher training college|teacher training institute|teachers|teaching certificate|classroom assistants|classroom instruction|classroom teaching|early childhood development|educators|elementary education|faith school|private school|refugee educator|school administrator|school authority|school director|school supervisor|state school|teaching assistant|teaching assistant|teaching assistants|accessible learning|alienation|asylum|asylum seeker|at.risk population|bachelor.s degree|bachelors degree|career.entry support|career entry support|career path training|church|community education|competency.based training|continuing education|continuing training|continuous professional development|degree|diploma|disabilities|disability|district.level|displaced person|displaced populations|education|education in emergencies|favela|fragility in education|gang members|geographically dispersed|in.service training|informal education|informal learning|informal training|language learning|learning community|master.s degree|masters|mathematics|migrant|minority ethnic group|mosque|moving populations|natural science|Non.formal education|non.formal learning|Postsecondary Education|pre.service training|professional continuing education|professional education|professional learning community|professional learning communities|professional qualification|professional re.education|professional studies|professional training|qualification|refugee education|refugee learning|science|science and technology|Science Technology Engineering and Applied Mathematics|Science Technology Engineering and Mathematics|special educational needs|SEN learner|SEN student|special educational needs and disabilities|special needs students|street children|students|students with disabilities|technical training|Technical and vocational education and training|Vocational training|young people)"],
    },

    "TE": {
        "regex": ["(CAI|CAL|FDL|ODEL|ODL|RLO|TETS|CMS|EMIS|FDR|LMS|MOOC|OER|TEL|VLE)", "(MOOCs)"],
        "iregex": ["(adaptive learning|asynchronous learning|computer assisted instruction|Computer assisted learning|computer based assessment|computer based instruction|computer.based instruction|computer managed instruction|computer mediated learning|computer.mediated learning|Computer supported collaborative learning|computer supported education|computer.supported education|Computer.assisted instructional programme|computerised learning|computerized learning|connected learning|digital.learning|distance learning|distance learning program|educational innovation|electronic classroom|e.tutor|Etutor|examination systems|flipped learning|free digital learning|gamification|instructional innovation|instructional technology|integrated learning systems|Intelligent agent|Intelligent tutoring system|media literacy|micro learning|micro.learning|microlearning|multimedia instruction|online course|online lab|online laboratory|online learning|online textbook|Online tutor|open learning|personalised teaching|Plasma.based instruction|Reusable learning object|School website|Synchronous online learning|Teacher development software|technological pedagogical content|Technology engagement teaching strategy|technology integration|tele education|tele.education|teleeducation|textbook analytics|virtual learning|Virtual school|web based instruction|web.based instruction|webinar|blended learning|computer.assisted instruction|Course Management System|Differentiated learning|digital learning|distance education|distributed learning|e.learning|elearning|electronic learning|EdTech|Education Technology|Educational Technology|Education Management Information System|Educational technologies|e textbook|e.textbook|electronic textbook|etextbook|electronic whiteboard|Emerging education technologies|Emerging education technology|flipped classroom|free digital resources|H.learning|hybrid learning|ICT in classrooms|ICT in the classroom|Individualised learning|Interactive learning environment|interactive whiteboard|ubiquitous learning|learning management system|Learning platform|massive open online course|m education|m.education|meducation|mobile education|m learning|m.learning|mlearning|Mobile learning|open educational resources|open and distance elearning|open and distance e.learning|open and distance learning|open education|personalised learning|Self.directed learning|self.paced learning|smart board|smartboard|technology assisted learning|technology at school|Technology enhanced learning|Technology.enhanced learning|technology in education|technology in school|technology use in education|technology.assisted learning|virtual classroom|virtual learning environment)"],
    },

    "TT": {
        "regex": ["(BADA|CMC|ICT|IOS|IoT|IT|QQ|RACHEL|TV|VR)"],
        "iregex": ["\y(app|Apple|blog|cloud|COWs|data|i.pad|intel|ipad|Maemo|MeeGo|QZone|radio|Viber|Web|WiFi|Ebook)\y", "(3D printer|3D printing|access to computers|accessible technologies|alternative communication|android|application|audio recording|augmentative communication|barriers to technology|big data|Blackberry|camera|cellphone|Chatbot|clicker technology|clickers|computational thinking literacy|computer illiteracy|computer literacy|Computer.mediated communication|computerised|computers on wheels|Connectivity|CT literacy|digital communication|digital content|digital exclusion|Digital immigrants|digital inclusion|Digital native|Digital scrapbook|digital storytelling|digital technology|digital transformation|digitalised|digitised|Discord|Disruptive technology|Douban|Douyin|DVD player|earphones|Facebook|game console|Garnet|Geographical information systems|hardware|headphones|holograms|ICT goods and services|inclusive technologies|influence of technology|Information communications technology literacy|information literacy|Instagram|instructional systems|instructional technology|integration of technology|interactive|Internet|internet access|internet domain|iphone|information technology|keyboard|kindle|laptop|LinkedIn|metadata|microsoft|new media|new technologies|offline|online|online discussion|online lab|open source|open source software|Open wedOS|operating system|Palm OS|Pinterest|platform|podcast|Poll Everywhere|printer|RACHEL server|Reddit|SD card|simulation|Sina Weibo|single board computer|Snapchat|social network|social networking sites|software|supportive technology|Symbian|technological literacy|technology leapfrogging|technology.enhanced|telephone|television|TikTok|Twitter|Verdict|video recorder|videoconferencing|virtual peer|Virtual reality|WeChat|Wikipedia|Windows|Youtube|moodle|digital skills|assistive technology|bandwidth|computer|digital divide|digital literacy|Digital resources|e.book|e.reader|ereader|gadget|information and communication technology|internet of things|mobile phone|Raspberry Pi|social media|tablet|WhatsApp)"],
    },

    "TT and PP": "TT AND PP",
    "TE or (TT and PP)": "TE OR (TT AND PP)",

    "Bangladesh": "Bangladesh",
    "Burkina Faso": "Burkina Faso",
    "Burundi": "Burundi",
    "Central African Republic": "Central African Republic",
    "Chad": "Chad",
    "Comoros": "Comoros",
    "Congo": "Congo",
    "Eritrea": "Eritrea",
    "Ethiopia": "Ethiopia",
    "Gambia": "Gambia",
    "Ghana": "Ghana",
    "Guinea.Bissau": "Guinea.Bissau",
    "India": "India",
    "Jordan": "Jordan",
    "Kenya": "Kenya",
    "Lebanon": "Lebanon",
    "Liberia": "Liberia",
    "Malawi": "Malawi",
    "Mali": "Mali",
    "Mozambique": "Mozambique",
    "Nepal": "Nepal",
    "Niger": "Niger",
    "Nigeria": "Nigeria",
    "Pakistan": "Pakistan",
    "Peru": "Peru",
    "Philippines": "Philippines",
    "Rwanda": "Rwanda",
    "Sierra Leone": "Sierra Leone",
    "South Sudan": "South Sudan",
    "Sudan": "Sudan",
    "Tanzania": "Tanzania",
    "Uganda": "Uganda",
    "Zambia": "Zambia",
    "Zimbabwe": "Zimbabwe",
}

KEYWORDS = {
"Countries": ["DRC","RSA","AFR","EAC","EAP","ECA","LAC","MENA","SIDS","SADC","SAR","SSA","LMIC","LMICs","Niger","Chad","Ghana","India","Kenya","Mali","Nepal","Niger","Peru","Sudan","Benin","China","Congo","Cuba","Egypt","Fiji","Gabon","Haiti","Iraq","Iraq","Laos","Libya","Burma","Nauru","Nauru","Syria","Tibet","Togo","Yemen","Bangladesh","Burkina Faso","Burundi","Central African Republic","Comoros","Congo","Eritrea","Ethiopia","Gambia","Guinea-Bissau","Jordan","Lebanon","Liberia","Malawi","Mozambique","Nigeria","Pakistan","Philippines","Rwanda","Sierra Leone","South Sudan","Tanzania","Uganda","Zambia","Zimbabwe","Abkhazia","Afghanistan","Algeria","Angola","Armenia","Artsakh","Nagorno-Karabakh","Azerbaijan","Belize","Bhutan","Bolivia","Plurinational State of Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Cambodia","Cameroon","Cabo Verde","Cape Verde","Central African Republic","Colombia","Republic of the Congo","Republic of the Congo","Costa Rica","Côte d'Ivoire","Ivory Coast","Democratic Republic of the Congo","Djibouti","Dominican Republic","East Timor","Timor L'este","Timor-L'este","Ecuador","El Salvador","El Salvador","Equatorial Guinea","eSwatini","Eswatini","Kingdom of Eswatini","Swaziland","Swaziland","Islamic republic of the Gambia","Republic of the Gambia","Guatemala","Guinea","Guinea","Guyana","Honduras","Indonesia","Jamaica","Kiribati","Kurdistan","Kyrgyzstan","Kyrgyzstan","Kyrgyzstan","Laos People's Democratic Republic","Lesotho","Liberia","Madagascar","Maldives","Maldives","Mauritania","Mauritius","Mauritius","Mexico","Federated States of Micronesia","Micronesia","Moldova","Republic of Moldova","Mongolia","Morocco","Myanmar","Namibia","Nicaragua","North Korea","North Macedonia","Rep. of Macedonia","Republic of North Macedonia","The former Yugoslav Republic of Macedonia","Palestine","Palestine, State of","State of Palestine","Panama","Papua New Guinea","Paraguay","Pridnestrovian Moldovan Republic","Transnistria","Puntland","Romania","Sahrawi Arab Democratic Republic","Sahrawi Republic","Western Sahara","Saint Lucia","Sao Tome and Principe","Sao Tome and Principe","Senegal","Serbia","Solomon Islands","Somalia","Somaliland","Republic of South Africa","South Africa","South Ossetia","the State of Alania","Sri Lanka","Suriname","Suriname","Syrian Arab Republic","Tajikistan","Tanzania","Thailand","Tunisia","Turkey","Turkmenistan","Tuvalu","Ukraine","Uzbekistan","Vanuatu","Bolivarian Republic of Venezuela","Venezuela","Viet Nam","Vietnam"],
"Regions": ["Africa","Arab world","Asia-Pacific","Caribbean","Central Africa","Central America","Central Asia","East Africa","East Africa Community","East Asia","East Asia and Pacific","Eastern Africa","Eastern Asia","Europe and Central Asia","Horn of Africa","Latin America","Latin America and Caribbean","Micronesia","Middle Africa","Middle East","Middle East and North Africa","North Africa","Northern Africa","Pacific","Polynesia","Small Island Development States","Southern African Development Community","South America","South Asia","South Asia Region","Southeast Asia","Southeastern Asia","Southern Africa","Southern Asia","Sub-Saharan Africa","West Africa","Western Africa","Western Asia"],
"Dterms": ["conflict affected areas","conflict-affected areas","conflict affected regions","conflict-affected regions","conflict zones","developing context","developing countries","developing country","developing economies","developing economy","developing market countries","developing market country","developing markets","developing nation","developing region","developing state","developing world","emergent nation","emergent nations","emerging economies","emerging market countries","emerging market country","emerging nation","emerging world","fragile and conflict affected areas","fragile and conflict affected regions","fragile areas","fragile state","fragile contexts","fragile regions","Global South","growing economies","less developed countries","less developed country","low and middle income countries","low income countries","low income country","low income environment","low resource countries","low resource country","low resource environment","low-income countries","low-income country","low-income environment","low-resource countries","low-resource country","low-resource environment","middle-income country","middle-income country","middle-income country","middle-income environment","middle income environment","third world","third-world","under developed countries","under developed country","under-developed countries","under-developed country","underdeveloped countries","underdeveloped country","under-developed nation","under developed nation","underdeveloped nation"]
}

AUTH_KEY = env("AUTH_KEY")
