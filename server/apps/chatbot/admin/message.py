from django.contrib import admin

from server.apps.chatbot.models import Message
from server.apps.core.admin import BaseModelAdmin


@admin.register(Message)
class MessageAdmin(BaseModelAdmin):
    list_display = (
        'conversation_title',
        'sender',
        'content_preview',
        'created_at',
    )
    list_filter = ('is_user', 'created_at', 'conversation')
    search_fields = ('content', 'conversation__title')
    ordering = ('-created_at',)

    @admin.display(
        description='Conversation',
        ordering='conversation__title',
    )
    def conversation_title(self, obj):
        return obj.conversation.title

    @admin.display(
        description='Sender',
        ordering='is_user',
    )
    def sender(self, obj):
        return 'User' if obj.is_user else 'Gemma 3 4B'

    @admin.display(description='Content')
    def content_preview(self, obj):
        return (
            obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        )

    # Custom fieldsets for better organization
    fieldsets = (
        (None, {'fields': ('conversation', 'is_user', 'content')}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
