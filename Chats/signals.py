from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    print("Signal triggered")  # Add this line to ensure the signal is being triggered
    if created:
        print("Signal",instance.user.id)
        channel_layer = get_channel_layer()
        notification_obj = Notification.objects.filter(is_seen=False, user=instance.user).count()
        username = instance.user.username
        data = {
            'count': notification_obj
        }

        async_to_sync(channel_layer.group_send)(
            username, {
                'type': 'send_notification',
                'value': json.dumps(data)
            }
        )