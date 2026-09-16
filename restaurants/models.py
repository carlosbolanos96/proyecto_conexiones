from django.conf import settings
from django.db import models


class Restaurant(models.Model):
    """Restaurant catalog owner and business location."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants', verbose_name='propietario')
    name = models.CharField(max_length=150, verbose_name='nombre')
    description = models.TextField(blank=True, verbose_name='descripción')
    address = models.ForeignKey('locations.Address', on_delete=models.PROTECT, related_name='restaurants', verbose_name='dirección')
    is_active = models.BooleanField(default=True, verbose_name='activo')

    class Meta:
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        constraints = [models.UniqueConstraint(fields=['owner', 'name'], name='unique_restaurant_per_owner')]

    def __str__(self):
        return self.name

# Create your models here.
