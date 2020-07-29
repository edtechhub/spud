"""spud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
	path('', include('publications.urls')),
	path('dgjhsdfiulganflidj/', admin.site.urls),
]

# Profiler initialization. It starts a daemon thread which continuously
# collects and uploads profiles. Best done as early as possible
import googlecloudprofiler
try:
    # service and service_version can be automatically inferred when
    # running on App Engine. project_id must be set if not running
    # on GCP.
    googlecloudprofiler.start(service='django_app', verbose=3)
except (ValueError, NotImplementedError) as exc:
    print(exc)  # Handle errors here