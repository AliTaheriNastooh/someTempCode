import json

from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from search_index.documents.post import PostDocument


class PostDocumentSerializer(DocumentSerializer):
    """Serializer for the Book document."""

    class Meta(object):
        """Meta options."""

        # Specify the correspondent document class
        document = PostDocument

        # List the serializer fields. Note, that the order of the fields
        # is preserved in the ViewSet.
        fields = (
            'messageId',
            'content',
            'messageDate',
            'elasticPushDate',
            'publication_date',
            'senderId',
            'senderUsername',
            'senderName',
            'isGroup',
            'channelId',
            'channelName',
            'channelUsername',
            'stock',
            'sentiment',
            'source',
            'image',
            'version',
            'parentId',
            'likeCount'
        )
