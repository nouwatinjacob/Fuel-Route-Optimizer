from rest_framework import serializers


class RouteRequestSerializer(serializers.Serializer):
    start_city = serializers.CharField()
    start_state = serializers.CharField()
    end_city = serializers.CharField()
    end_state = serializers.CharField()
