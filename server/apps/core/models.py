import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_currentuser.db.models import CurrentUserField
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class UUIDModel(models.Model):
    """
    An abstract base class model that provides a UUID field.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``modified_at`` fields.
    """

    created_at = AutoCreatedField(_('created'))
    modified_at = AutoLastModifiedField(_('modified'))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Overriding the save method in order to make sure that
        modified field is updated even if it is not given as
        a parameter to the update field argument.
        """
        if update_fields := kwargs.get('update_fields'):
            kwargs['update_fields'] = set(update_fields).union({'modified_at'})

        super().save(*args, **kwargs)


class ValidateOnSaveMixin:
    """
    By default, Django models do not validate on save!
    Django model mixin to force Django to validate (i.e. call `full_clean`) before `save`

    More info:
    * "Why doesn't django's model.save() call full clean?"
        https://stackoverflow.com/questions/4441539/
    * "Model-level validation" at Django developers Google group
        https://groups.google.com/g/django-developers/c/RHTR8stBsr8/m/BnasXKYKBwAJ
    """

    def save(self, force_insert=False, force_update=False, **kwargs):  # noqa: FBT002
        if not (force_insert or force_update):
            self.full_clean()  # Will raise ValidationError if needed
        super().save(force_insert, force_update, **kwargs)


class CreatedByMixin(models.Model):
    created_by = CurrentUserField(
        to='users.User',
        related_name='%(app_label)s_%(class)s_created',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Created by'),
    )

    class Meta:
        abstract = True


class ModifiedByMixin(models.Model):
    modified_by = CurrentUserField(
        to='users.User',
        related_name='%(app_label)s_%(class)s_modified',
        on_delete=models.SET_NULL,
        on_update=True,
        verbose_name=_('Modified by'),
    )

    class Meta:
        abstract = True

    def get_modified_by_display(self):
        result = '-'
        if self.modified_by:
            result = self.modified_by.get_full_name()
        return result


class AuditModel(CreatedByMixin, ModifiedByMixin):
    class Meta:
        abstract = True


class BaseModel(AuditModel, UUIDModel, TimeStampedModel):
    """
    Abstract base class for all models in the core app.
    """

    class Meta:
        abstract = True


class UpdateMethodMixin(models.Model):
    class Meta:
        abstract = True

    def update(self, **kwargs: 'Any') -> 'models.Model':  # noqa: F821
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.save(update_fields=kwargs.keys())

        return self
