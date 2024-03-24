from rest_framework import serializers

from ..models import FriendList, User
from ..users.serializers import *



class FrindListSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    friends = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = FriendList
        fields = ['id', 'user', 'friends']
    # print(friends)
    
    def create(self, validated_data):
     friends_data = validated_data.pop('friends')
     user = User.objects.create(**validated_data)
     for friend_data in friends_data:
        friend = User.objects.create(**friend_data)
        user.friends.add(friend)
     return user

