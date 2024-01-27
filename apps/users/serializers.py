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
                  'username', 'name', 'register_data', 'image']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number',
                  'username', 'name', 'register_data', 'image',]


class UserSerializer(serializers.ModelSerializer):
    # image = serializers.ImageField(use_url=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number',
                  'username', 'password',  'name', 'register_data', 'is_active', 'image', 'is_deleted']

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
