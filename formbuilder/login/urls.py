from django.conf.urls import url
from login import views


urlpatterns = [
    url(r'^login/$', views.login_view, name="login"),
    url(r'^home/$', views.home, name='home'),
    url(r'^logout/$', views.logout, name='logout'),
]




