from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

import clowder_account.urls
import clowder_server.urls

urlpatterns = [
    url(r'', include(clowder_account.urls)),
    url(r'', include(clowder_server.urls)),
    url(r'^about/', TemplateView.as_view(template_name='about.html')),
    url(r'^$', TemplateView.as_view(template_name='home.html')),
    url(r'^admin/', include(admin.site.urls)),
]
