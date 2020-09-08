from rest_framework import serializers


class SampleSerializer(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()