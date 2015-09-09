from django.conf.urls import patterns, url
from imagestore import settings
from api import views

urlpatterns = patterns(
    '',
    url(r'^populate$', views.populate),
    url(r'^images/f$', views.image_list_force_reload, name="image_list_reload"),
    url(r'^images/$', views.ImageList.as_view(), name="image_list"),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
)
