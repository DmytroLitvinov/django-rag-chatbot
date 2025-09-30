from django.db import models

from server.apps.chatbot.choices import ConversationTypeChoices
from server.apps.chatbot.managers import ConversationManager
from server.apps.core.models import BaseModel


class Conversation(BaseModel):
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='conversations'
    )

    documents = models.ManyToManyField(
        'documents.Document', blank=True, related_name='conversations'
    )

    title = models.CharField(max_length=200, default='New Chat')
    type = models.CharField(
        max_length=50,
        choices=ConversationTypeChoices.choices,
        default=ConversationTypeChoices.CHAT,
    )

    objects = ConversationManager()

    class Meta:
        ordering = ['-modified_at']
        indexes = [
            models.Index(fields=['-modified_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def message_count(self):
        """Get the total number of messages in this conversation"""
        return self.messages.count()

    @property
    def last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.last()

    @property
    def is_document_type(self) -> bool:
        """Check if the conversation is of document type"""
        return self.type == ConversationTypeChoices.DOCUMENT

    @property
    def is_chat_type(self) -> bool:
        """Check if the conversation is of chat type"""
        return self.type == ConversationTypeChoices.CHAT

    def get_context_messages(self, limit=10):
        """Get recent messages for context"""
        return list(self.messages.all()[:limit])
