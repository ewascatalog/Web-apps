from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from catalog import views

handler404 = 'views.page_not_found'
handler500 = 'views.error'

urlpatterns = [
    url(r'^$', views.catalog_home, name='catalog_home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^information/$', views.catalog_info, name='catalog_info'),
    url(r'^input/$', views.catalog_study, name='catalog_study'),
    url(r'^input/(?P<pk>\w+?)/analysis/$', views.catalog_analysis, name='catalog_analysis'),
    url(r'^input/(?P<pk>\w+?)/participants/$', views.catalog_participants, name='catalog_participants'),
    url(r'^input/(?P<pk>\w+?)/results/$', views.catalog_results, name='catalog_results'),
    url(r'^input/(?P<pk>\w+?)/results/import/$', views.catalog_import, name='catalog_import'),
]


