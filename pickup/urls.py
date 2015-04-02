from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pickup.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'event.views.signup', name='home'),

    url(r'^admin/', include(admin.site.urls)),
)
