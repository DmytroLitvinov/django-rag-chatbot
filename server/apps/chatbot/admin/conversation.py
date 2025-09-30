from django.contrib import admin
from django.db.models import Count
from server.apps.chatbot.models import Conversation
from server.apps.core.admin import BaseModelAdmin


@admin.register(Conversation)
class ConversationAdmin(BaseModelAdmin):
    list_display = ("title", "get_message_count", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)

    def get_message_count(self, obj):
        return obj.messages.count()

    get_message_count.short_description = "Messages"
    get_message_count.admin_order_field = "messages__count"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(messages__count=Count("messages"))
        return queryset
