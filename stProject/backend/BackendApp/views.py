from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_QUERY_IN,
    SUGGESTER_COMPLETION,
    LOOKUP_QUERY_STARTSWITH,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    DefaultOrderingFilterBackend,
    FilteringFilterBackend,
    SearchFilterBackend,
    SuggesterFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from BackendApp.documents import PostDocument
from BackendApp.serializers import PostDocumentSerializer


class PostViewSet(DocumentViewSet):
    document = PostDocument
    serializer_class = PostDocumentSerializer
    ordering = ('stock_symbol',)
    lookup_field = 'stock_symbol'

    filter_backends = [
        DefaultOrderingFilterBackend,
        FilteringFilterBackend,
        SearchFilterBackend,
        SuggesterFilterBackend,
    ]

    search_fields = (
        'stock_symbol',
        'content',
    )

    filter_fields = {
        'content': {
            'field': 'content',
            'lookups': [
                LOOKUP_QUERY_IN,
            ],
        },
        'stock_symbol': 'stock_symbol',
    }

    suggester_fields = {
        'stock_symbol_suggest': {
            'field': 'stock_symbol.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
            'options': {
                'size': 20,  # Override default number of suggestions
            },
        },
    }