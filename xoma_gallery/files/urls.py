from django.conf.urls.defaults import *

urlpatterns = patterns('files.views',
    (r'^(?P<contents_pk>\d+)(\.\w{3,4})$', 'get_file'),
)