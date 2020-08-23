from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from elasticsearch_dsl import analyzer

from posts.models import post
from posts.models.post import Post

#INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])
INDEX = Index('djangopost')

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


@INDEX.doc_type
class PostDocument(Document):
    messageId = fields.IntegerField()
    content = fields.TextField()
    messageDate = fields.DateField()
    elasticPushDate = fields.DateField()
    senderId = fields.IntegerField()
    senderUsername = fields.KeywordField()
    senderName = fields.KeywordField()
    isGroup = fields.BooleanField()
    channelId = fields.IntegerField()
    channelName = fields.KeywordField()
    channelUsername = fields.KeywordField()
    parentId = fields.IntegerField()
    likeCount = fields.IntegerField()
    source = fields.KeywordField()
    sentiment = fields.KeywordField()
    stock = fields.TextField(
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    image = fields.TextField()
    version = fields.KeywordField()

    class Django(object):
        model = Post
