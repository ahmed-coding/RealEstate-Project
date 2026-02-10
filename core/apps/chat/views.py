
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from urllib.parse import urlencode
import json
from itertools import chain
from datetime import datetime
import pytz

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.authtoken.models import Token

from ..models import PrivateChatRoom, RoomChatMessage, User, FriendList, find_or_create_private_chat


def private_chat_room_view(request, *args, **kwargs):
    room_id = request.GET.get("room_id")
    user = request.user
    if not user.is_authenticated:
        base_url = reverse('login')
        query_string = urlencode({'next': f"/chat/?room_id={room_id}"})
        url = f"{base_url}?{query_string}"
        return redirect(url)

    context = {}

    context['m_and_f'] = get_recent_chatroom_messages(user)

    if room_id:
        context["room_id"] = room_id
    return render(request, "chat/room.html", context)


def get_recent_chatroom_messages(user):
    """
    sort in terms of most recent chats (users that you most recently had conversations with)
    """
    # 1. Find all the rooms this user is a part of
    rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
    rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

    # 2. merge the lists
    rooms = list(chain(rooms1, rooms2))

    # 3. find the newest msg in each room
    m_and_f = []
    for room in rooms:
        # Figure out which user is the "other user" (aka friend)
        if room.user1 == user:
            friend = room.user2
        else:
            friend = room.user1

        # Check if FriendList exists for the user
        try:
            friend_list = FriendList.objects.get(user=user)
            is_friend = friend_list.is_mutual_friend(friend)
        except FriendList.DoesNotExist:
            # Create friend list if it doesn't exist
            friend_list = FriendList.objects.create(user=user)
            is_friend = False

        # find newest msg from that friend in the chat room
        try:
            message = RoomChatMessage.objects.filter(
                room=room).order_by('-timestamp').first()
        except RoomChatMessage.DoesNotExist:
            message = None

        if message:
            m_and_f.append({
                'message': message,
                'friend': friend
            })
        else:
            # Create a placeholder for rooms with no messages
            from django.utils import timezone
            placeholder_message = RoomChatMessage(
                user=friend,
                room=room,
                timestamp=timezone.now(),
                content="No messages yet"
            )
            m_and_f.append({
                'message': placeholder_message,
                'friend': friend
            })

    # Sort by timestamp, most recent first
    from django.utils import timezone
    sorted_result = sorted(
        m_and_f, key=lambda x: x['message'].timestamp if x['message'].timestamp else timezone.now(), reverse=True)

    return sorted_result


@method_decorator(csrf_exempt, name='dispatch')
class ChatViewSet(ViewSet):
    """
    ViewSet for Chat operations with CSRF exemption
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/chat/ - List all chat rooms for the authenticated user
        """
        user = request.user
        rooms_data = get_recent_chatroom_messages(user)

        result = []
        for item in rooms_data:
            room = item['message'].room
            friend = item['friend']
            message = item['message']

            result.append({
                'id': room.id,
                'chatroom_id': room.id,
                'other_user': {
                    'id': friend.id,
                    'name': friend.name or friend.username or friend.email,
                    'username': friend.username,
                    'image': friend.image.url if friend.image else None,
                },
                'last_message': message.content if message.content else 'No messages yet',
                'last_message_ts': message.timestamp.isoformat() if message.timestamp else None,
                'unread_count': 0,
                'is_active': room.is_active,
            })

        return Response(result)

    def create(self, request):
        """
        POST /api/chat/ - Create or return a private chat room
        """
        user1 = request.user
        user2_id = request.data.get("userId") or request.data.get("user2_id")

        if not user2_id:
            return Response({
                'response': 'user2_id is required',
                'chatroom_id': None
            }, status=400)

        try:
            user2 = User.objects.get(pk=user2_id)
            chat = find_or_create_private_chat(user1, user2)
            print("Successfully got the chat")
            return Response({
                'response': "Successfully got the chat.",
                'chatroom_id': chat.id
            })
        except User.DoesNotExist:
            return Response({
                'response': "Unable to start a chat with that user.",
                'chatroom_id': None
            }, status=404)


# Keep the old function-based views for reference (may be removed later)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_chat_rooms(request):
    """
    API endpoint to list all chat rooms for the authenticated user
    """
    user = request.user
    rooms_data = get_recent_chatroom_messages(user)

    result = []
    for item in rooms_data:
        room = item['message'].room
        friend = item['friend']
        message = item['message']

        result.append({
            'id': room.id,
            'chatroom_id': room.id,
            'other_user': {
                'id': friend.id,
                'name': friend.name or friend.username or friend.email,
                'username': friend.username,
                'image': friend.image.url if friend.image else None,
            },
            'last_message': message.content if message.content else 'No messages yet',
            'last_message_ts': message.timestamp.isoformat() if message.timestamp else None,
            'unread_count': 0,
            'is_active': room.is_active,
        })

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_return_private_chat(request, *args, **kwargs):
    """
    API endpoint to create or return a private chat room
    """
    user1 = request.user
    user2_id = request.data.get("user2_id") or request.data.get("userId")

    if not user2_id:
        return Response({
            'response': 'user2_id is required',
            'chatroom_id': None
        }, status=400)

    try:
        user2 = User.objects.get(pk=user2_id)
        chat = find_or_create_private_chat(user1, user2)
        print("Successfully got the chat")
        return Response({
            'response': "Successfully got the chat.",
            'chatroom_id': chat.id
        })
    except User.DoesNotExist:
        return Response({
            'response': "Unable to start a chat with that user.",
            'chatroom_id': None
        }, status=404)
