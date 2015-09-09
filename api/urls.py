from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from imagestore import settings
from api import views

urlpatterns = patterns(
    '',
    url(r'^populate$', views.populate),
    url(r'^optimize$', views.optimize),
    url(r'^f/images$', views.image_list_force_reload, name="image_list_reload"),
    url(r'^images/$', views.ImageList.as_view(), name="image_list"),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
)

urlpatterns = format_suffix_patterns(urlpatterns)
