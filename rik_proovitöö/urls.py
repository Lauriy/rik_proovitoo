from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from rik_proovitöö.views import homepage, legal_entity_detail, establish_llc

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', homepage, name='homepage'),
    path('establish-an-lcc', establish_llc, name='establish_llc'),
    path('legal-entity/<int:code>/', legal_entity_detail, name='legal_entity_detail'),

]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
