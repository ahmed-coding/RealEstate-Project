from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, FriendList


@receiver(post_save, sender=User)
def user_save(sender, instance, **kwargs):
    FriendList.objects.get_or_create(user=instance)
