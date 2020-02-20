from django.db import models
from django.utils.translation import ugettext_lazy as _

class Post(models.Model):

    SOURCES = (('tl', 'telegram'), ('sy', 'sahamyab'),)
    SENTIMENTS = ('up' , 'down' , 'stable')
    VERSIONS = ('v1',)
    content = models.TextField(
        _('content'),
    )
    date = models.DateTimeField(
        _('date'),
    )
    sender_id = models.CharField(
        _('sender id'),
        max_length=100,
    )
    sender_username = models.CharField(
        _('sender username'),
        max_length=100,
    )
    sender_name = models.CharField(
        _('sender name'),
        max_length=100,
         blank=True, null=True
    )
    is_group = models.BooleanField(
        _('is group'),
    )
    channel_username = models.CharField(
        _('channel username'),
        max_length=100,
    )
    channel_name = models.CharField(
        _('channel name'),
        max_length=100,
        blank=True, null=True
    )
    source = models.CharField(
        _('source'),
        max_length=2,
    )
    stock_symbol = models.CharField(
        _('stock symbol'),
        max_length=20,
    )
    sentiment = models.CharField(
        _('sentiment'),
        max_length=6,
    )
    like_count = models.IntegerField(
        _('like count'),
         blank=True, null=True

    )
    parent_content = models.TextField(
        _('parent content'),
         blank=True, null=True
    )
    version = models.CharField(
        _('version'),
        max_length=2,
    )
