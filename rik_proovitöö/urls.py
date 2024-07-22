from django.conf import settings
from django.contrib import admin
from django.urls import path

from rik_proovitöö.views import homepage, set_language, legal_entity_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('set_language/', set_language, name='set_language'),
    path('', homepage, name='homepage'),
    path('legal-entity/<int:code>/', legal_entity_detail, name='legal_entity_detail'),

]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
