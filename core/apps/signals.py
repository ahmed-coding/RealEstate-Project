from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import FriendRequest, Notification, PrivateChatRoom, UnreadChatRoomMessages, User, FriendList

# create user frindlist


@receiver(post_save, sender=User)
def user_save(sender, instance, **kwargs):
    FriendList.objects.get_or_create(user=instance)

# create notifications


@receiver(post_save, sender=FriendRequest)
def create_notification(sender, instance, created, **kwargs):
    if created:
        instance.notifications.create(
            target=instance.receiver,
            from_user=instance.sender,
            verb=f"{instance.sender.username} sent you a friend request.",
            content_type=instance,
        )

# chat signals


@receiver(post_save, sender=PrivateChatRoom)
def create_unread_chatroom_messages_obj(sender, instance, created, **kwargs):
    if created:
        unread_msgs1 = UnreadChatRoomMessages(
            room=instance, user=instance.user1)
        unread_msgs1.save()

        unread_msgs2 = UnreadChatRoomMessages(
            room=instance, user=instance.user2)
        unread_msgs2.save()


@receiver(pre_save, sender=UnreadChatRoomMessages)
def increment_unread_msg_count(sender, instance, **kwargs):
    """
    When the unread message count increases, update the notification. 
    If one does not exist, create one. (This should never happen)
    """
    if instance.id is None:  # new object will be created
        pass  # create_unread_chatroom_messages_obj will handle this scenario
    else:
        previous = UnreadChatRoomMessages.objects.get(id=instance.id)
        if previous.count < instance.count:  # if count is incremented
            content_type = ContentType.objects.get_for_model(instance)
            if instance.user == instance.room.user1:
                other_user = instance.room.user2
            else:
                other_user = instance.room.user1
            try:
                notification = Notification.objects.get(
                    target=instance.user, content_type=content_type, object_id=instance.id)
                notification.verb = instance.most_recent_message
                notification.timestamp = timezone.now()
                notification.save()
            except Notification.DoesNotExist:
                instance.notifications.create(
                    target=instance.user,
                    from_user=other_user,
                    # we want to go to the chatroom
                    verb=instance.most_recent_message,
                    content_type=content_type,
                )


@receiver(pre_save, sender=UnreadChatRoomMessages)
def remove_unread_msg_count_notification(sender, instance, **kwargs):
    """
    If the unread messge count decreases, it means the user joined the chat. So delete the notification.
    """
    if instance.id is None:  # new object will be created
        pass  # create_unread_chatroom_messages_obj will handle this scenario
    else:
        previous = UnreadChatRoomMessages.objects.get(id=instance.id)
        if previous.count > instance.count:  # if count is decremented
            content_type = ContentType.objects.get_for_model(instance)
            try:
                notification = Notification.objects.get(
                    target=instance.user, content_type=content_type, object_id=instance.id)
                notification.delete()
            except Notification.DoesNotExist:
                pass
                # Do nothing
