from django.conf.urls import url
from builder import views


urlpatterns = [
    url(r'^ajax/forms/(\d+)/$', views.formtemplate_details_ajax, name='formtemplate_details_ajax'),
    url(r'^ajax/recaptcha_check/$', views.recaptcha_check_ajax, name='recaptcha_check_ajax'),
    url(r'^forms/(\d+)/$', views.formtemplate_details, name='formtemplate_details'),
    url(r'^results/(\d+)/$', views.formtemplate_results, name='formtemplate_results'),
]
