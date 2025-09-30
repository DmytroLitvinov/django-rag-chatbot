from django.db import models

from server.apps.core.models import BaseModel


class Message(BaseModel):
    conversation = models.ForeignKey(
        'chatbot.Conversation', on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    is_user = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'}: {self.content[:50]}..."

    @property
    def role(self):
        """Get the role for Ollama API"""
        return "user" if self.is_user else "assistant"

    @property
    def truncated_content(self):
        """Get truncated content for display"""
        return (
            self.content[:100] + "..."
            if len(self.content) > 100
            else self.content
        )
