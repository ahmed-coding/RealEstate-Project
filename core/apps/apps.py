from django.apps import AppConfig


class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self) -> None:
        from . import algolia_serializers
        from .signals import user_save, create_notification, create_unread_chatroom_messages_obj, increment_unread_msg_count, remove_unread_msg_count_notification, create_notification_messages_brodcast
        user_save
        create_notification
        create_unread_chatroom_messages_obj
        increment_unread_msg_count
        remove_unread_msg_count_notification
        create_notification_messages_brodcast
        return super().ready()
