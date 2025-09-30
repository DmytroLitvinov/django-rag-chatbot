from django.contrib import admin


__all__ = ('BaseModelAdmin',)


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'created_at', 'modified_at', 'created_by', 'modified_by')
