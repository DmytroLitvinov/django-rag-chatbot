from django.contrib import admin
from django.db.models import Count

from server.apps.chatbot.models import Conversation
from server.apps.core.admin import BaseModelAdmin


@admin.register(Conversation)
class ConversationAdmin(BaseModelAdmin):
    list_display = ('title', 'get_message_count', 'created_at', 'modified_at')
    list_filter = ('created_at', 'modified_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'modified_at')
    ordering = ('-modified_at',)

    @admin.display(
        description='Messages',
        ordering='messages__count',
    )
    def get_message_count(self, obj):
        return obj.messages.count()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(messages__count=Count('messages'))
        return queryset
