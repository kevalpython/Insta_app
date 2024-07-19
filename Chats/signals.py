from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification,Message
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    
    if created:
        
        channel_layer = get_channel_layer()
        notification_obj = Notification.objects.filter(is_seen=False, user=instance.user)
        notification_count = notification_obj.count()  
        username = instance.user.username
        data = {
            'count': notification_count
        }

        async_to_sync(channel_layer.group_send)(
            username, {
                'type': 'send_notification',
                'value': json.dumps(data)
            }
        )
       
        
    else:
        channel_layer = get_channel_layer()
        notification_obj = Notification.objects.filter(is_seen=False, user=instance.user)
        notification_count = notification_obj.count()
 
        username = instance.user.username
        data = {
            'count': notification_count
        }

        async_to_sync(channel_layer.group_send)(
            username, {
                'type': 'send_notification',
                'value': json.dumps(data)
            }
        )
        
    
@receiver(post_save, sender=Message)
def send_notification(sender, instance, created, **kwargs):
    if created:

        channel_layer = get_channel_layer()
        message_obj = Message.objects.filter(
            is_seen=False, conversation=instance.conversation, sender=instance.sender
        )
 
        message_useen_count = message_obj.count()
       
        data = {"message_useen_count": message_useen_count}

        async_to_sync(channel_layer.group_send)(
            f"messages_{instance.conversation}",
            {"type": "send_messge_notification_count", "value": json.dumps(data)},
        )

    else:

        channel_layer = get_channel_layer()
        message_obj = Message.objects.filter(
            is_seen=False, conversation=instance.conversation, sender=instance.sender
        )

        message_useen_count = message_obj.count()
        
        data = {"message_useen_count": message_useen_count}

        async_to_sync(channel_layer.group_send)(
            f"messages_{instance.conversation}",
            {"type": "send_messge_notification_count", "value": json.dumps(data)},
        )