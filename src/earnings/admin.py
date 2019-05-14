from django.contrib import admin
from django.db.models import Count, Sum, Min, Max, DateTimeField
from django.db.models.functions import Trunc
from import_export.admin import ImportExportModelAdmin

from .models import Balance, SoldSoftwares, SaleSummary

# Register your models here.

admin.site.register(Balance)


def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return 'hour'
    if date_hierarchy + '__month' in request.GET:
        return 'day'
    if date_hierarchy + '__year' in request.GET:
        return 'week'
    return 'day'


@admin.register(SoldSoftwares)
class SalesAdmin(ImportExportModelAdmin):
    pass


@admin.register(SaleSummary)
class SaleSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sale_summary_change_list.html'
    date_hierarchy = 'timestamp'

    list_filter = (
        'category',
    )

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
            'total_sales': Sum('sold_price'),
        }

        response.context_data['summary'] = list(
            qs
                .values('category')
                .annotate(**metrics)
                .order_by('-total_sales')
        )

        # List view summary

        response.context_data['summary_total'] = dict(qs.aggregate(**metrics))

        # Chart

        period = get_next_in_date_hierarchy(request, self.date_hierarchy)
        response.context_data['period'] = period

        summary_over_time = qs.annotate(
            period=Trunc('timestamp', 'day', output_field=DateTimeField()),
        ).values('period').annotate(total=Sum('sold_price')).order_by('period')
        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        response.context_data['summary_over_time'] = [{
            'period': x['period'],
            'total': x['total'] or 0,
            'pct': \
                ((x['total'] or 0) - low) / (high - low) * 100
                if high > low else 0,
        } for x in summary_over_time]

        return response


