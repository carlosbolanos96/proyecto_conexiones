from django.conf import settings
from django.db import models


class Address(models.Model):
    """Delivery or business address owned by a user."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses', verbose_name='propietario')
    street = models.CharField(max_length=150, verbose_name='calle')
    number = models.CharField(max_length=20, verbose_name='número')
    city = models.CharField(max_length=100, verbose_name='ciudad')
    province = models.CharField(max_length=100, verbose_name='provincia')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='código postal')
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='latitud')
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='longitud')
    is_default = models.BooleanField(default=False, verbose_name='predeterminada')

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['city', 'street', 'number']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['city']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['owner'],
                condition=models.Q(is_default=True),
                name='one_default_address_per_user',
            ),
        ]

    def __str__(self):
        return f'{self.street} {self.number}, {self.city}'

# Create your models here.
