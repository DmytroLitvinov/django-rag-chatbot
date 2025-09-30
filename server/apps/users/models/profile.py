from typing import final
import uuid

from django.db import models

from simple_history.models import HistoricalRecords

from server.apps.core.models import BaseModel
from server.apps.users.choices import GenderChoices


@final
class Profile(BaseModel):
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='profile',
    )

    gender = models.CharField(choices=GenderChoices.choices, max_length=10, blank=True)

    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4))
