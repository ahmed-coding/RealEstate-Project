from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .notifications.utils import LazyNotificationEncoder

from .notifications.constants import CHAT_MSG_TYPE_GET_NEW_NOTIFICATIONS
from .models import Alarm, FriendRequest, Notification, PrivateChatRoom, Property, UnreadChatRoomMessages, User, FriendList
from firebase_admin import firestore

# Get a Firestore client
db = firestore.client()

# create user frindlist and migrate it to firebase


@receiver(post_save, sender=User)
def user_save(sender, instance, created, **kwargs):
    FriendList.objects.get_or_create(user=instance)
    data = {
        'userId': instance.id,
        'phoneNumber': instance.phone_number,
        'imageUrl': instance.get_profile_image_filename,
        'fullName': instance.name,
        'userType': instance.user_type,
    }
    doc_ref = db.collection("Users").document(
        str(data["userId"])).set(data, merge=True)
    print(doc_ref)


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


# notification signals

@receiver(post_save, sender=Notification)
def create_notification_messages_brodcast(sender, instance, created, **kwargs):
    if created:
        s = LazyNotificationEncoder()
        channel_layer = get_channel_layer()
        notifications = s.serialize([instance])
        async_to_sync(channel_layer.group_send)(
            f"notification_{instance.target.unique_no}",
            {
                'type': 'send_new_chat_notifications_payload',
                "chat_msg_type": CHAT_MSG_TYPE_GET_NEW_NOTIFICATIONS,
                'notifications': notifications,
            },
        )


@receiver(pre_save, sender=Property)
def create_notification_on_property_save(sender, instance, **kwargs):
    """
    Signal receiver function to create notifications when a property is saved.
    """
    old = Property.objects.filter(id=instance.id).first()
    if instance.is_active == True and old.is_active == False:  # Check if a new property is updated

        for_rent = True if instance.for_sale == False else False
        alarms = Alarm.objects.filter(
            state=instance.address.state,
            category=instance.category,
            is_active=True,
            # for_sale=instance.for_sale,
            # for_rent=instance.for_rent,
            min_price__lte=instance.price,
            max_price__gte=instance.price,
        )
        # for alarm in alarms:
        #     alarm_values = alarm.alarm_value.all()
        #     property_values = instance.property_value.all()
        #     matching_values = []
        #     for alarm_value in alarm_values:
        #         for property_value in property_values:
        #             if alarm_value.attribute == property_value.attribute and alarm_value.value == property_value.value.value:
        #                 matching_values.append(alarm_value)
        #                 break

        #     if len(matching_values) == len(alarm_values):
        #         # Create notification
        #         alarm.send_notification()

        for alarm in alarms:
            alarm_values = alarm.alarm_value.all()
            property_values = instance.property_value.all()

            # Get all attributes associated with the property
            property_attributes = set(
                pv.value.attribute for pv in property_values
            )

            # Check if all attribute values of the alarm are satisfied by the property
            if alarm_values.count() == len(property_attributes):
                matched_values = alarm_values.filter(
                    attribute__in=property_attributes,
                    value__in=[pv.value.value for pv in property_values]
                )

                if matched_values.count() == alarm_values.count():
                    # Create notification
                    # alarm.send_notification()
                    Notification.objects.create(
                        target=alarm.user,
                        from_user=None,  # You may set this to a specific user if needed
                        verb="Your alarm matched a new property!",
                        timestamp=timezone.now(),
                        content_type=ContentType.objects.get_for_model(
                            Alarm),  # Use Alarm model content type
                        object_id=alarm.id,  # Pass the ID of the alarm
                        content_object=alarm,  # Pass the alarm instance
                    )
