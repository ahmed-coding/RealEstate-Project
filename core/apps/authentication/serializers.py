from rest_framework.authtoken.models import Token
from rest_framework import serializers
from ..models import User
from rest_framework.authtoken.views import ObtainAuthToken, AuthTokenSerializer


class UserSerializer(serializers.ModelSerializer):
    # image = serializers.ImageField(use_url=True)
    password = serializers.CharField(write_only=True)
    user_auth = serializers.SerializerMethodField(read_only=True)

    def get_user_auth(self, obj):
        # request = self.context.get('request' or None)
        # serializer = AuthTokenSerializer(data=request.data,
        #                                  context=self.context)
        # serializer.is_valid(raise_exception=True)
        # user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=obj)
        return {
            'token': token.key,
            'user_id': obj.pk,
            'email': obj.email
        }

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number',
                  'username', 'password',  'name', 'image', 'user_auth']

    def create(self, validated_data):

        password = validated_data.pop("password", None)
        instence = self.Meta.model(**validated_data)
        if instence is not None:
            instence.set_password(password)
        instence.save()
        return instence
