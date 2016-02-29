from django.conf.urls import url
from builder import views

urlpatterns = [
    url(r'^form/([0-9])/json/$', views.json_formtemplate),
]
