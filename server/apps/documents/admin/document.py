from django.contrib import admin

from server.apps.core.admin import BaseModelAdmin
from server.apps.documents.models import Document


@admin.register(Document)
class DocumentAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'title',
        'user',
        'status',
        'processed_at',
        'created_at',
    )
    list_filter = ('status', 'processed_at', 'created_at')
    search_fields = ('title', 'description', 'file')
    readonly_fields = BaseModelAdmin.readonly_fields + (
        'status',
        'processed_at',
        'created_at',
        'modified_at',
    )
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
