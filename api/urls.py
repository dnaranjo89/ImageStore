from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from imagestore import settings
from api import views

urlpatterns = patterns(
    '',
    url(r'^images/$', views.get_image_list),
    url(r'^populate$', views.populate),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
)

urlpatterns = format_suffix_patterns(urlpatterns)
