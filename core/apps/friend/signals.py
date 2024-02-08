from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from ..models import  FriendRequest

@receiver(post_save, sender=FriendRequest)
def create_notification(sender, instance, created, **kwargs):
    if created:
        instance.notifications.create(
            target=instance.receiver,
            from_user=instance.sender,
            verb=f"{instance.sender.username} sent you a friend request.",
            content_type=instance,
        )
