from django_elasticsearch_dsl import Index
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl import  fields
from BackendApp.models import Post
from django_elasticsearch_dsl.registries import registry

post_index = Index('posts')
post_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)

@post_index.document
@registry.register_document
class PostDocument(Document):
    content = fields.TextField(
        attr='content',
    )
    date = fields.DateField(
        attr='date',
    )
    sender_id = fields.KeywordField(
        attr='sender_id'
    )
    sender_username = fields.TextField(
        attr='sender_username'
    )
    sender_name = fields.TextField(
        attr='sender_name'
    )
    is_group = fields.BooleanField(
        attr='is_group'
    )
    channel_username = fields.TextField(
        attr='channel_username'
    )
    channel_name = fields.TextField(
        attr='channel_name'
    )
    source = fields.TextField(
        attr='source'
    )
    stock_symbol = fields.TextField(
        attr='stock_symbol',
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'suggest': fields.CompletionField(),
        }
    )
    sentiment = fields.TextField(
        attr='sentiment'
    )
    like_count = fields.IntegerField(
        attr='like_count'
    )
    parent_content = fields.TextField(
        attr='parent_content'
    )
    version = fields.TextField(
        attr='version'
    )

    class Django:
        model = Post
        fields = [
            # 'date',
            # 'content',
            # 'sender_id',
            # 'sender_username',
            # 'sender_name',
            # 'is_group',
            # 'channel_username',
            # 'channel_name',
            # 'source',
            # 'sentiment',
            # 'like_count',
            # 'parent_content',
            # 'version',
        ]

