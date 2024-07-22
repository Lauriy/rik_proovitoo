from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import translation

from .forms import LegalEntitySearchForm
from .models import LegalEntity


def homepage(request):
    form = LegalEntitySearchForm(request.GET or None)
    people_results = []
    company_results = []
    limit = int(request.GET.get('limit', settings.SEARCH_RESULTS_INITIAL_LIMIT))
    max_limit = settings.SEARCH_RESULTS_MAX_LIMIT

    if form.is_valid():
        query = form.cleaned_data['query']
        people_results = LegalEntity.objects.filter(
            (Q(name__icontains=query) | Q(code__icontains=query)), is_person=True
        )[:limit]
        company_results = LegalEntity.objects.filter(
            (Q(name__icontains=query) | Q(code__icontains=query)), is_person=False
        )[:limit]

    return TemplateResponse(request, 'home.html', {
        'form': form,
        'people_results': people_results,
        'company_results': company_results,
        'limit': limit,
        'max_limit': max_limit,
    })


def legal_entity_detail(request, code: int):
    legal_entity = get_object_or_404(LegalEntity.objects.prefetch_related('stakes__stakeholder', 'holdings__company'),
                                     code=code)

    return TemplateResponse(request, 'legal_entity_detail.html', {
        'legal_entity': legal_entity
    })


def set_language(request):
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        if lang_code and lang_code in dict(settings.LANGUAGES).keys():
            translation.activate(lang_code)
            # request.session[translation.LANGUAGE_SESSION_KEY] = lang_code  # Use the correct import

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
