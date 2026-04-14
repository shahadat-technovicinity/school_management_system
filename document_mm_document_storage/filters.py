import django_filters
from .models import Document


class DocumentFilter(django_filters.FilterSet):
    """
    Figma Screen 1 এর সব filter এখানে আছে।
    GET /api/documents/?cabinet=2&status=available&days=30
    """
    cabinet  = django_filters.NumberFilter(field_name='cabinet__id')
    shelf    = django_filters.NumberFilter(field_name='shelf__id')
    status   = django_filters.ChoiceFilter(choices=Document.Status.choices)
    days     = django_filters.NumberFilter(method='filter_last_n_days', label='Last N days')
    location = django_filters.CharFilter(field_name='cabinet__location', lookup_expr='icontains')

    def filter_last_n_days(self, queryset, name, value):
        from django.utils import timezone
        from datetime import timedelta
        since = timezone.now() - timedelta(days=int(value))
        return queryset.filter(updated_at__gte=since)

    class Meta:
        model  = Document
        fields = ['cabinet', 'shelf', 'status', 'document_type', 'days', 'location']