from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework import serializers

from core.apps.models import Notification


class NotificationsSerializers(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"


class LazyNotificationEncoder(Serializer):
    """
    Serialize a Notification into JSON. 
    There are 3 types
            1. FriendRequest
            2. FriendList
            3. UnreadChatRoomMessage
    """

    def get_dump_object(self, obj):
        dump_object = {}
        if obj.get_content_object_type() == "FriendRequest":
            dump_object.update(
                {'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update(
                {'is_active': str(obj.content_object.is_active)})
            dump_object.update({'is_read': str(obj.read)})
            dump_object.update(
                {'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                # 'actions': {
                # 	# 'redirect_url': str(obj.redirect_url),
                # },
                "from": {
                    "image_url": str(obj.from_user.get_profile_image_filename if obj.from_user else "")
                }
            })
        if obj.get_content_object_type() == "FriendList":
            dump_object.update(
                {'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update(
                {'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'is_read': str(obj.read)})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                "from": {
                    "image_url": str(obj.from_user.get_profile_image_filename if obj.from_user else "")
                }
            })
        if obj.get_content_object_type() == "UnreadChatRoomMessages":
            dump_object.update(
                {'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update(
                {'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({

                "from": {
                    "title": str(obj.content_object.get_other_user.username or obj.content_object.get_other_user.name),
                    "image_url": str(obj.content_object.get_other_user.get_profile_image_filename)
                }
            })

        return dump_object
