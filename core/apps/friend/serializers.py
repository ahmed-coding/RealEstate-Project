from django.db.models import Q
from rest_framework import serializers

from ..models import FriendList, PrivateChatRoom, UnreadChatRoomMessages, User
from ..users.serializers import UserSerializer


class FrindsSerializers(UserSerializer):
    unread_messages = serializers.SerializerMethodField(read_only=True)
    # user = serializers.SerializerMethodField(read_only=True)

    # def get_user(self, obj) -> UserSerializer:
    #     user = self.context.get('user', None)
    #     room = self.context.get('room', None)
    #     chat = PrivateChatRoom.objects.get(id=room) or None
    #     if chat.user1 == user:
    #         ser = UserSerializer(instance=obj).validate()
    #     else:
    #         ser = UserSerializer(instance=user).validate()
    #     return ser

    def get_unread_messages(self, obj) -> int:
        user = self.context.get('user' or None)

        room = PrivateChatRoom.objects.filter(
            Q(user1=user, user2=obj) | Q(user1=obj, user2=user)
        )
        try:
            unread_count = UnreadChatRoomMessages.objects.get(
                user=obj).count
        except UnreadChatRoomMessages.DoesNotExist:
            unread_count = 0
        return unread_count

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number',
                  'username', 'password',  'name', 'register_data', 'is_active', 'image', 'is_deleted', 'unread_messages',]


class FrindListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=None)
    friends = FrindsSerializers(many=True)

    class Meta:
        model = FriendList
        fields = ['id', 'friends', 'user']
    # print(friends)

    # def get_user(self, obj) -> UserSerializer:
    #     user = self.context.get('user', None)
    #     room = self.context.get('room', None)
    #     chat = PrivateChatRoom.objects.get(id=room) or None
    #     if chat.user1 == user:
    #         ser = UserSerializer(instance=obj).validate()
    #     else:
    #         ser = UserSerializer(instance=user).validate()
    #     return ser

    def validate(self, attrs):
        attrs['user'] = self.context.get('user', None)
        self.frinds.context = self.context
        # self.frinds.context['room'] = attrs['id']
        return super().validate(attrs)

    # def create(self, validated_data):
    #     friends_data = validated_data.pop('friends')
    #     user = User.objects.create(**validated_data)
    #     for friend_data in friends_data:
    #         friend = User.objects.create(**friend_data)
    #         user.friends.add(friend)
    #     return user
