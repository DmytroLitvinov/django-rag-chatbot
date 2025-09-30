from django.db import models

class ConversationManager(models.Manager):
    """Custom manager for Conversation model"""

    def recent(self, limit=5):
        """Get recent conversations"""
        return self.get_queryset().order_by('-updated_at')[:limit]

    def with_messages(self):
        """Get conversations with prefetched messages"""
        return self.get_queryset().prefetch_related('messages')

    def create_with_message(self, message_content):
        """Create a conversation with an initial message"""
        title = (
            message_content[:50] + "..."
            if len(message_content) > 50
            else message_content
        )
        conversation = self.create(title=title)
        conversation.messages.create(content=message_content, is_user=True)
        return conversation
