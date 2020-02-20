from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from BackendApp.documents import PostDocument


class PostDocumentSerializer(DocumentSerializer):
    class Meta:
        document = PostDocument
        fields = (
            'id',
            'content',
            'date',
            'sender_id',
            'sender_username',
            'sender_name',
            'is_group',
            'channel_username',
            'channel_name',
            'source',
            'stock_symbol',
            'sentiment',
            'like_count',
            'parent_content',
            'version',
        )