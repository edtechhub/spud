from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('showrecord/', views.showrecord, name='showrecord'),
    path('ris_export/', views.ris_export, name='ris_export'),
    path('zotero_export/', views.zotero_export, name='zotero_export'),
    path('keywords/', views.keywords, name='keywords'),
]
