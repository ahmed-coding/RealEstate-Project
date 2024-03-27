from rest_framework import serializers

from ..models import Banner


class BannerSerializers(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"
        model = Banner
