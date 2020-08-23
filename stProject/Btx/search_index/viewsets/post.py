from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_EXCLUDE,
)
from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import (
    # ...
    SuggesterFilterBackend,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet, DocumentViewSet
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination

from search_index.documents.post import PostDocument
from search_index.serializers.post import PostDocumentSerializer


class PostDocumentView(DocumentViewSet):
    """The BookDocument view."""

    document = PostDocument
    serializer_class = PostDocumentSerializer
    pagination_class = PageNumberPagination

    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
        SuggesterFilterBackend,
    ]
    # Define search fields
    search_fields = (
        'content',
        'senderName',
        'senderUsername',
        'channelName',
        'channelUsername',
        'sentiment',
        'source',
        'stock'
    )
    filter_fields = {

        'source': 'source',
        'channelName': 'channelName',
        'channelUsername': 'channelUsername',
        'stock': 'stock',
        'senderName': 'senderName',
        'senderUsername': 'senderUsername',
        'sentiment': 'sentiment',
        'content': {
            'field': 'content',
            'lookups': [
                LOOKUP_QUERY_IN,
            ]
        },
        'messageDate': {
            'field': 'messageDate',
            'lookups': [
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LTE,
            ]
        },
        'elasticPushDate': {
            'field': 'elasticPushDate',
            'lookups': [
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LTE,
            ]
        },
    }

    suggester_fields = {
        'stock_suggest': {
            'field': 'stock.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
            'options': {
                'size': 20,  # Override default number of suggestions
                # 'skip_duplicates': True,  # Whether duplicate suggestions should be filtered out.
            },
        }
    }

    ordering_fields = {

        'stock': 'stock.raw',
        'channelId': 'channelId',
        'messageDate': 'messageDate',
    }
    # Specify default ordering
    ordering = ('messageDate', 'channelId',)
