from django.apps import AppConfig


class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self) -> None:
        from .signals import user_save, create_notification, create_unread_chatroom_messages_obj, increment_unread_msg_count, remove_unread_msg_count_notification
        user_save
        create_notification
        create_unread_chatroom_messages_obj
        increment_unread_msg_count
        remove_unread_msg_count_notification
        return super().ready()
