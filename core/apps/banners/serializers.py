from rest_framework import serializers

from ..models import Banner


class BannerSerializers(serializers.ModelSerializer):
    time_created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', read_only=True)
    end_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', read_only=True)
    start_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', read_only=True)

    class Meta:
        fields = "__all__"
        model = Banner
