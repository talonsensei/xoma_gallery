from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

# mod_wsgi does NOT pass the '/ri' mount point to this application. However,
# the django development server does. So in order to get these urls.py to
# work correctly with both, I created a match group that doesn't create a 
# back reference. That match group is this: (?:ri/)?

urlpatterns = patterns('',
    
    # Admin sites are doing some reverse url lookup, and the match group trick
    # doesn't work with them.  To resolve this issue we create two references:
    # one for mod_wsgi, and the other for the development server.
    (r'^admin/', include(admin.site.urls)),
  #  (r'^admin/(.*)',    admin.site.root),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^xoma_gallery/contest/admin/', include(admin.site.urls)),
    (r'^xoma_gallery/contest/admin/doc/', include('django.contrib.admindocs.urls')),
   # (r'^xoma_gallery/contest/admin/(.*)', admin.site.urls),
    # db files
    (r'^xoma_gallery/contest/files/', include('xoma_gallery.files.urls')),
    # contest links
    (r'^xoma_gallery/contest/$', 'xoma_gallery.photos.views.index'),
    (r'^xoma_gallery/contest/(?P<contest_id>\d+)/$', 'xoma_gallery.photos.views.show_contest'),
    (r'^xoma_gallery/contest/(?P<contest_id>\d+)/results/$', 'xoma_gallery.photos.views.show_results'),
    (r'^xoma_gallery/contest/rate/(?P<entry_id>\d+)/$', 'xoma_gallery.photos.views.rate'),
    # account related links
    (r'^xoma_gallery/contest/login/$', 'django.contrib.auth.views.login'),
    (r'^xoma_gallery/contest/logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'^xoma_gallery/contest/denied/$', 'django.views.generic.simple.direct_to_template', {'template': 'denied.html'}),
    # for legacy link (this was the old start page)
    (r'^xoma_gallery/contest/gallery/$', 'django.views.generic.simple.redirect_to', {'url': '/xoma_gallery/contest/'}),
    (r'^xoma_gallery/contest/decider', 'xoma_gallery.decider.views.decision'),
)


# Media files when using the development server
if not settings.DJANGO_ENV == 'PRODUCTION':
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^xoma_gallery/contest/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.STATIC_ROOT }),
    )
