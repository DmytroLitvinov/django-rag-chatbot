import secrets
import string
import uuid
from typing import final

import structlog
from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook
from simple_history.models import HistoricalRecords

from server.apps.core.models import BaseModel
from server.apps.users.constants import (
    USER_FIRST_NAME_MAX_LENGTH,
    USER_LAST_NAME_MAX_LENGTH,
)

logger = structlog.get_logger()

__all__ = ('User',)


@final
class User(BaseModel, LifecycleModel, AbstractUser):
    # Optimistic concurrency protection
    version = IntegerVersionField()

    first_name = models.CharField(
        _('first name'), max_length=USER_FIRST_NAME_MAX_LENGTH, blank=True
    )
    last_name = models.CharField(
        _('last name'), max_length=USER_LAST_NAME_MAX_LENGTH, blank=True
    )

    history = HistoricalRecords(
        history_id_field=models.UUIDField(default=uuid.uuid4),
    )

    def __str__(self):
        return f'{self.__class__.__name__} {self.id} | {self.username}'

    @hook(AFTER_CREATE)
    def create_profile(self):
        from server.apps.users.models import Profile  # noqa: PLC0415

        Profile.objects.create(user=self)

    @staticmethod
    def generate_random_password():
        alphabet = string.ascii_letters + string.digits
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3
            ):
                break
        return password

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret
