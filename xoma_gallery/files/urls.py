from django.conf.urls.defaults import *

urlpatterns = patterns('xoma_gallery.files.views',
    (r'^(?P<contents_pk>\d+)(\.\w{3,4})$', 'get_file'),
)