from django.contrib import admin
from server.apps.chatbot.models import Message
from server.apps.core.admin import BaseModelAdmin


@admin.register(Message)
class MessageAdmin(BaseModelAdmin):
    list_display = ("conversation_title", "sender", "content_preview", "timestamp")
    list_filter = ("is_user", "timestamp", "conversation")
    search_fields = ("content", "conversation__title")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)

    def conversation_title(self, obj):
        return obj.conversation.title

    conversation_title.short_description = "Conversation"
    conversation_title.admin_order_field = "conversation__title"

    def sender(self, obj):
        return "User" if obj.is_user else "Gemma 3 4B"

    sender.short_description = "Sender"
    sender.admin_order_field = "is_user"

    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    content_preview.short_description = "Content"

    # Custom fieldsets for better organization
    fieldsets = (
        (None, {"fields": ("conversation", "is_user", "content")}),
        ("Timestamps", {"fields": ("timestamp",), "classes": ("collapse",)}),
    )
