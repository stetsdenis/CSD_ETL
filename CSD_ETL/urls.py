"""
URL configuration for CSD_ETL project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,re_path
from flow.views import *

urlpatterns = [
    path('admin/', admin.site.urls),                                                #landing admin django
    path('login/',login_handler,name='login_hadler'),                               #start login
    re_path(r'^login/(?P<provider>\w+)/$', login_handler, name='login_hadler'),     #login, gestione con CP per callback
    path('get-cookies/', csrf_token, name='csrf_token'),                            #get cookies per chiamate POST
    path('startOauth/', startAuthentication, name = 'startAuthentication'),         #inizio autenticazione
    path('get_dimensions/', get_dimensions, name='get_dimensions'),                 #prendi dimensioni 
    path('get_metrics/', get_metrics, name='get_metrics'),                          #....e metriche per creare flow
    path('startFlow/',start_flow, name='start_flow'),                               #inizio creazione flow
    path('finalize/', createFlow, name = 'createFlow'),                             #lancia crezione del flow vera e propria
    path('success/', redirectSuccess, name = 'redirectSuccess')                     #rimanda a pagina di successo
]
