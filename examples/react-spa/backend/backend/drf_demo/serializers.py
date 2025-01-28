from rest_framework import serializers


class AddSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
