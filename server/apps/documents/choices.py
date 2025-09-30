from django.db import models
from django.utils.translation import gettext_lazy as _


class RagBackendChoices(models.TextChoices):
    OPENAI = 'openai', 'OpenAI'
    OLLAMA = 'ollama', 'Ollama'


class DocumentStatusChoices(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Processing')
    COMPLETED = 'COMPLETED', _('Completed')
    FAILED = 'FAILED', _('Failed')
