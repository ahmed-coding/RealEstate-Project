from celery import shared_task
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task
def testTask(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notification",
        {
            "type": "send_notification",
            "message": message,
            "message1": "Test Message from notification Task"
        }
    )
