from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from .admin import LegalEntityForm
from .forms import LegalEntitySearchForm, PublicEquityFormSet
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
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(stakes__stakeholder__name__icontains=query) |
            Q(stakes__stakeholder__code__icontains=query),
            is_person=False
        ).distinct()[:limit]

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


def establish_llc(request):
    if request.method == 'POST':
        form = LegalEntityForm(request.POST, exclude_is_person=True)
        formset = PublicEquityFormSet(request.POST, instance=LegalEntity())
        form.equity_formset = formset

        if form.is_valid() and formset.is_valid():
            legal_entity = form.save(commit=False)
            if formset.is_valid():
                formset.instance = legal_entity
                legal_entity.save()
                formset.save()

                return redirect('legal_entity_detail', code=legal_entity.code)
    else:
        form = LegalEntityForm(exclude_is_person=True)
        formset = PublicEquityFormSet(instance=LegalEntity())
        form.equity_formset = formset

    return TemplateResponse(request, 'establish_llc.html', {'form': form, 'formset': formset})


def edit_llc(request, code):
    legal_entity = get_object_or_404(LegalEntity, code=code)
    if request.method == 'POST':
        form = LegalEntityForm(request.POST, instance=legal_entity, exclude_is_person=True)
        formset = PublicEquityFormSet(request.POST, instance=legal_entity)
        form.equity_formset = formset

        if form.is_valid() and formset.is_valid():
            form.save()
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.pk:  # New equity holder
                    instance.is_founding = False
                instance.save()
            formset.save_m2m()

            return redirect('legal_entity_detail', code=legal_entity.code)
    else:
        form = LegalEntityForm(instance=legal_entity, exclude_is_person=True)
        formset = PublicEquityFormSet(instance=legal_entity)
        form.equity_formset = formset

    return TemplateResponse(request, 'edit_llc.html', {'form': form, 'formset': formset,
                                                       'legal_entity': legal_entity})
