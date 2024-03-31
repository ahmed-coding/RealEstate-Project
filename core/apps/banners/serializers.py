from rest_framework import serializers

from ..models import Banner
from django.utils import timezone


class BannerSerializers(serializers.ModelSerializer):
    time_created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', read_only=True)
    end_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', read_only=True)
    start_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', read_only=True)
    
    def validate_end_time(self, date):
        """
        Validate that the end time is not in the past.
        """
        if date < timezone.now():
            raise serializers.ValidationError("End time must be in the future.")
        return date
        

    class Meta:
        fields = "__all__"
        model = Banner
