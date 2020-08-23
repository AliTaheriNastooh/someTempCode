from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext as _

from .models.post import Post


class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class StockFilter(InputFilter):
    parameter_name = 'stock'
    title = _('Stock')

    def queryset(self, request, queryset):
        if self.value() is not None:
            stock = self.value()

            return queryset.filter(
                Q(stock=stock)
            )


class SenderNameFilter(InputFilter):
    parameter_name = 'senderName'
    title = _('Sender Name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            senderName = self.value()

            return queryset.filter(
                Q(senderName=senderName)
            )



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('messageId', 'content', 'senderName', 'channelName', 'stock', 'sentiment', 'source')
    search_fields = ('stock', 'sentiment', 'senderName', 'channelName', 'source')
    list_filter = (StockFilter, SenderNameFilter, 'sentiment', 'source')
