from django.conf.urls import url
from builder import views, view_utils


urlpatterns = [
    #url(r'^ajax/forms/(\d+)/$', views.formtemplate_details_ajax, name='formtemplate_details_ajax'),
    url(r'^ajax/recaptcha_check/$', view_utils.recaptcha_check_ajax, name='recaptcha_check_ajax'),
    url(r'^(?P<category>[\w-]+)/forms/(?P<slug>[\w-]+)/$', views.formtemplate_details, name='formtemplate_details'),
    url(r'^results/(\d+)/$', views.formtemplate_results, name='formtemplate_results'),
    url(r'^query/$', views.formresponse_query, name='formresponse_query'),
    url(r'^menu/$', views.category_menu, name='category_menu'),
]
