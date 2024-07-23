from django.apps import AppConfig


class ChatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Chats'

    def ready(self) -> None:
        import Chats.signals

