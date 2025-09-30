from django.core.validators import FileExtensionValidator
from django.db import models
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook

from server.apps.core.models import BaseModel
from server.apps.documents.choices import DocumentStatusChoices

__all__ = ('Document',)


class Document(LifecycleModel, BaseModel):
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='documents'
    )

    title = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=400, blank=True)
    file = models.FileField(
        upload_to='documents/', validators=[FileExtensionValidator(['pdf'])]
    )

    status = models.CharField(
        max_length=50,
        choices=DocumentStatusChoices.choices,
        default=DocumentStatusChoices.PENDING,
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    @hook(AFTER_CREATE)
    def after_create(self):
        from server.apps.documents.tasks import ingest_document_task

        ingest_document_task.enqueue(self.id)
