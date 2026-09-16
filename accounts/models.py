from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Profile(models.Model):
    """Role profile attached to Django's default user model."""

    class Role(models.TextChoices):
        CONSUMER = 'consumer', 'Consumidor'
        PRODUCER = 'producer', 'Productor'
        COURIER = 'courier', 'Transportador'
        WAREHOUSE_MANAGER = 'warehouse_manager', 'Encargado de bodega'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', verbose_name='usuario')
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.CONSUMER, verbose_name='rol')
    phone = models.CharField(max_length=30, blank=True, verbose_name='teléfono')
    avatar = models.URLField(blank=True, verbose_name='avatar')
    default_address = models.ForeignKey(
        'locations.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_for_profiles',
        verbose_name='dirección predeterminada',
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['user__username']
        indexes = [models.Index(fields=['role'])]

    def clean(self):
        super().clean()
        if self.default_address_id and self.default_address.owner_id != self.user_id:
            raise ValidationError({'default_address': 'Default address must belong to the profile user.'})

    def __str__(self):
        return f'{self.user.username} ({self.role})'

# Create your models here.
