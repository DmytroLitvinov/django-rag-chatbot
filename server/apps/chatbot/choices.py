from django.db import models


class ConversationTypeChoices(models.TextChoices):
    CHAT = 'chat', 'Chat'
    DOCUMENT = 'document', 'Document'
