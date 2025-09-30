import secrets
import string
from typing import final
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from concurrency.fields import IntegerVersionField
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook
from simple_history.models import HistoricalRecords
import structlog

from server.apps.core.models import TimeStampedModel, BaseModel
from server.apps.users.constants import USER_FIRST_NAME_MAX_LENGTH, USER_LAST_NAME_MAX_LENGTH


logger = structlog.get_logger()

__all__ = ('User',)


@final
class User(BaseModel, LifecycleModel, AbstractUser):
    # Optimistic concurrency protection
    version = IntegerVersionField()

    first_name = models.CharField(_('first name'), max_length=USER_FIRST_NAME_MAX_LENGTH, blank=True)
    last_name = models.CharField(_('last name'), max_length=USER_LAST_NAME_MAX_LENGTH, blank=True)

    # SUPPLIER SIGNUP FIELDS
    # (for new registration of Supplier)
    is_supplier_signup = models.BooleanField(default=False)
    is_finished_supplier_signup = models.BooleanField(default=False)
    # CUSTOMER SIGNUP FIELDS
    is_customer_signup = models.BooleanField(default=False)
    is_finished_customer_signup = models.BooleanField(default=False)

    internal_info = models.TextField(blank=True)

    history = HistoricalRecords(
        history_id_field=models.UUIDField(default=uuid.uuid4),
    )

    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return f'{self.__class__.__name__} {self.id} | {self.username}'

    @hook(AFTER_CREATE)
    def create_profile(self):
        from server.apps.users.models import Profile

        Profile.objects.create(user=self)

    @staticmethod
    def generate_random_password():
        alphabet = string.ascii_letters + string.digits
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3  # noqa: PLR2004
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
