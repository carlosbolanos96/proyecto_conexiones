from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Producer(models.Model):
    """Agro business data for a producer profile."""

    profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE, related_name='producer', verbose_name='perfil')
    business_name = models.CharField(max_length=150, verbose_name='nombre del negocio')
    tax_id = models.CharField(max_length=30, unique=True, verbose_name='CUIT')
    address = models.ForeignKey('locations.Address', on_delete=models.PROTECT, related_name='producers', verbose_name='dirección')
    description = models.TextField(blank=True, verbose_name='descripción')

    class Meta:
        verbose_name = 'Productor'
        verbose_name_plural = 'Productores'
        ordering = ['business_name']
        indexes = [models.Index(fields=['business_name'])]

    def clean(self):
        super().clean()
        if self.profile_id and self.profile.role != 'producer':
            raise ValidationError({'profile': 'Producer profile must have producer role.'})

    def __str__(self):
        return self.business_name


class Product(models.Model):
    """Agro product sold by quantity and unit."""

    class Unit(models.TextChoices):
        KG = 'kg', 'Kilogramo'
        BOX = 'box', 'Caja'
        UNIT = 'unit', 'Unidad'

    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='products', verbose_name='productor')
    name = models.CharField(max_length=120, verbose_name='nombre')
    description = models.TextField(blank=True, verbose_name='descripción')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='precio')
    unit = models.CharField(max_length=20, choices=Unit.choices, verbose_name='unidad')
    is_active = models.BooleanField(default=True, verbose_name='activo')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
        indexes = [
            models.Index(fields=['producer']),
            models.Index(fields=['name']),
        ]
        constraints = [models.UniqueConstraint(fields=['producer', 'name'], name='unique_product_per_producer')]

    def __str__(self):
        return f'{self.name} ({self.unit})'

# Create your models here.
