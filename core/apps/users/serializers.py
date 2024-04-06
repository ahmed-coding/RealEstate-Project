from django.db.models import Avg
from rest_framework import serializers
from ..models import User


# class UserSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'


class UpdateUserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(allow_empty_file=True, use_url=True)
    email = serializers.EmailField(allow_blank=True)
    # age = serializers.IntegerField(allow_blank=True, )
    phone_number = serializers.CharField(allow_blank=True, )
    username = serializers.CharField(allow_blank=True, )
    register_data = serializers.CharField(allow_blank=True, read_only=True)
    name = serializers.CharField(allow_blank=True, )

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number',
                  'username', 'name', 'register_data', 'image', 'user_type']


class UserProfileSerializer(serializers.ModelSerializer):
    count_review = serializers.SerializerMethodField(read_only=True)
    reting = serializers.SerializerMethodField(read_only=True)
    sold_property = serializers.SerializerMethodField(read_only=True)
    property_count = serializers.SerializerMethodField(read_only=True)

    def get_count_review(self, obj) -> int:
        properties = obj.property.all()
        total_reviews = 0

        for property in properties:
            total_reviews += property.review.count()

        return total_reviews

    def get_reting(self, obj) -> int:
        # average_rating = obj.review.aggregate(Avg('rate_review'))[
        #     'rate_review__avg']
        # return average_rating if average_rating else 0.0

        properties = obj.property.all()
        total_rating = 0.0
        total_properties = 0

        for property in properties:
            avg_rating = property.review.aggregate(Avg('rate_review'))[
                'rate_review__avg']
            if avg_rating:
                total_rating += avg_rating
                total_properties += 1

        return total_rating / total_properties if total_properties > 0 else 0.0

    def get_sold_property(self, obj) -> int:
        return obj.property.filter(is_active=False).count()

    def get_property_count(self, obj) -> int:
        return obj.property.all().count()

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number',
                  'username', 'name', 'register_data', 'image', 'user_type', 'count_review', 'reting', 'sold_property', 'property_count']


class UserSerializer(serializers.ModelSerializer):
    # image = serializers.ImageField(use_url=True)
    password = serializers.CharField(write_only=True)
    # property_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number',
                  'username', 'password',  'name', 'register_data', 'is_active', 'image', 'is_deleted', 'user_type']

    def create(self, validated_data):

        password = validated_data.pop("password", None)
        instence = self.Meta.model(**validated_data)
        if instence is not None:
            instence.set_password(password)
        instence.save()
        return instence


# class NotificationSerializer(serializers.ModelSerializer):
#     time_created = serializers.DateTimeField(
#         format='%Y-%m-%d %H:%M', read_only=True)

#     class Meta:
#         model = Notification
#         fields = ("id", "title", "text", "time_created", "is_readed")
#         # exclude = ('user',)
