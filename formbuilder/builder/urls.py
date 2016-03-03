from django.conf.urls import url
from builder import views


urlpatterns = [
    url(r'^(\w+)/forms/(\d+)/$', views.formtemplate_details, name='formtemplate_details'),
    url(r'^(\w+)/results/(\d+)/$', views.formtemplate_results, name='formtemplate_results'),
]
