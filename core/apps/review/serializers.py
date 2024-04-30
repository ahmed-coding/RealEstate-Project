from rest_framework import serializers
from ..models import Review


class ReviewSerializers(serializers.ModelSerializer):
    user = serializers.IntegerField(read_only=True)

    def validate(self, attrs):
        # self.user = self.context.get('user').id
        attrs['user'] = self.context.get('user')
        return super().validate(attrs)

    def to_representation(self, instance):
        user = self.context.get('user' or None)
        # is_likes = instance.review_likes.filter(
        #     user=user).exists()
        # likes = instance.review_likes.all().count()
        r = 0.0
        image = instance.user.image.url if instance.user.image else ''
        if instance.user.rate.filter(prop=instance.prop).exists():
            r = instance.user.rate.get(
                prop=instance.prop).rate
        formatted_review_date = instance.time_created.strftime(
            '%Y-%m-%d %H:%M')

        date = {
            'id': instance.id,
            'user': f"{instance.user.get_full_name()}",
            'time_created': formatted_review_date,
            'review': instance.review,
            'rating': instance.rate_review,
            'profile': image,
            # 'likes_count': likes,
            # 'is_liked': is_likes

        }
        return date

    class Meta:
        model = Review
        fields = '__all__'


class CreateReviewSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(default=None)

    def validate(self, attrs):
        # self.user = self.context.get('user').id
        attrs['user'] = self.context.get('user')
        return super().validate(attrs)

    class Meta:
        model = Review
        fields = '__all__'
