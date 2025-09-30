from django.contrib import admin

from server.apps.core.admin import BaseModelAdmin
from server.apps.documents.models import DocumentChunk


@admin.register(DocumentChunk)
class DocumentChunkAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'document',
        'page_number',
        'chunk_index',
        'tokens',
    )
    list_filter = ('document', 'page_number')
    search_fields = ('content',)
    readonly_fields = BaseModelAdmin.readonly_fields + (
        'embedding',
        'created_at',
        'modified_at',
    )
    ordering = ('document', 'page_number', 'chunk_index')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('document')
