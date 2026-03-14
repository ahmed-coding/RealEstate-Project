from rest_framework.authtoken.models import Token
from rest_framework import serializers
from ..models import User
from rest_framework.authtoken.views import ObtainAuthToken, AuthTokenSerializer


class EmailAuthTokenSerializer(serializers.Serializer):
    """
    Custom serializer that accepts email instead of username for login.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")

            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials")

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")

            attrs["user"] = user
        else:
            raise serializers.ValidationError("Must include email and password")

        return attrs


class UserAuthSerializer(serializers.ModelSerializer):
    # image = serializers.ImageField(use_url=True)
    password = serializers.CharField(write_only=True)
    user_auth = serializers.SerializerMethodField(read_only=True)

    def get_user_auth(self, obj) -> dict:
        # request = self.context.get('request' or None)
        # serializer = AuthTokenSerializer(data=request.data,
        #                                  context=self.context)
        # serializer.is_valid(raise_exception=True)
        # user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=obj)
        return {"token": token.key, "user_id": obj.pk, "email": obj.email}

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "username",
            "password",
            "name",
            "image",
            "user_auth",
            "user_type",
            "device_token",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instence = self.Meta.model(**validated_data)
        if instence is not None:
            instence.set_password(password)
        instence.save()
        return instence


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No user is associated with this email address"
            )
        return value


class PasswordResetSerializer(serializers.Serializer):
    # token = serializers.CharField()
    email = serializers.EmailField()
    new_password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Invalid token")
        return data
