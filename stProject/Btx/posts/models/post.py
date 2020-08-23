import json
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

SOURCE_TELEGRAM = 'telegram'
SOURCE_SAHAMYAB = 'sahamyab'
SOURCE_CHOICES = (
    (SOURCE_TELEGRAM, 'Telegram'),
    (SOURCE_SAHAMYAB, 'Sahamyab')
)

SENTIMENT_NEUTRAL = 'neutral'
SENTIMENT_POSITIVE = 'positive'
SENTIMENT_NEGATIVE = 'negative'
SENTIMENT_CHOICES = (
    (SENTIMENT_NEUTRAL, 'Neutral'),
    (SENTIMENT_NEGATIVE, 'Negative'),
    (SENTIMENT_POSITIVE, 'Positive')
)


class Post(models.Model):
    messageId = models.IntegerField(null=False)
    content = models.TextField(null=False, blank=False)
    messageDate = models.DateTimeField()
    elasticPushDate = models.DateTimeField()
    senderId = models.IntegerField()
    senderUsername = models.CharField(max_length=200, null=True, blank=True)
    senderName = models.CharField(max_length=200)
    isGroup = models.BooleanField()
    channelId = models.IntegerField()
    channelName = models.CharField(max_length=200)
    channelUsername = models.CharField(max_length=200, null=True, blank=True)
    parentId = models.IntegerField(null=True, blank=True)
    likeCount = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=100, choices=SOURCE_CHOICES)
    stock = models.CharField(max_length=100)
    sentiment = models.CharField(max_length=100, choices=SENTIMENT_CHOICES)
    image = models.TextField(null=True, blank=True)
    version = models.CharField(max_length=20)

    class Meta(object):
        ordering = ["messageId"]

    def __str__(self):
        return self.stock

