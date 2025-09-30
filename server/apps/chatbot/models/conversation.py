from django.db import models

from server.apps.chatbot.managers import ConversationManager
from server.apps.core.models import BaseModel


class Conversation(BaseModel):
    title = models.CharField(max_length=200, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ConversationManager()

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=['-updated_at']),
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

    def get_context_messages(self, limit=10):
        """Get recent messages for context"""
        return list(self.messages.all()[:limit])
