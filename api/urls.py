from django.conf.urls import patterns, url
from imagestore import settings
from api import views

urlpatterns = patterns(
    '',
    url(r'^images/$', views.ImageList.as_view()),
)
