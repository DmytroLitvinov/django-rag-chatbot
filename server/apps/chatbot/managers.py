from django.db import models

from server.apps.chatbot.choices import ConversationTypeChoices


class ConversationQuerySet(models.QuerySet):
    def filter_chat_type(self):
        return self.filter(type=ConversationTypeChoices.CHAT)

    def filter_document_type(self):
        return self.filter(type=ConversationTypeChoices.DOCUMENT)

    def recent(self, limit=5):
        """Get recent conversations"""
        return self.order_by('-modified_at')[:limit]


class ConversationManager(models.Manager):
    """Custom manager for Conversation model"""

    def get_queryset(self):
        return ConversationQuerySet(self.model, using=self._db)

    def filter_chat_type(self):
        return self.get_queryset().filter_chat_type()

    def filter_document_type(self):
        return self.get_queryset().filter_document_type()

    def recent(self, limit=5):
        """Get recent conversations"""
        return self.get_queryset().recent(limit=limit)

    def with_messages(self):
        """Get conversations with prefetched messages"""
        return self.get_queryset().prefetch_related('messages')

    def create_with_message(self, message_content):
        """Create a conversation with an initial message"""
        title = (
            message_content[:50] + '...'
            if len(message_content) > 50
            else message_content
        )
        conversation = self.create(title=title)
        conversation.messages.create(content=message_content, is_user=True)
        return conversation
