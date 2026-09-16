from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class RestaurantProduct(models.Model):
    """Menu item sold by a restaurant."""

    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='menu_items', verbose_name='restaurante')
    name = models.CharField(max_length=120, verbose_name='nombre')
    description = models.TextField(blank=True, verbose_name='descripción')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='precio')
    is_available = models.BooleanField(default=True, verbose_name='disponible')

    class Meta:
        verbose_name = 'Plato'
        verbose_name_plural = 'Platos'
        ordering = ['restaurant__name', 'name']
        indexes = [
            models.Index(fields=['restaurant']),
            models.Index(fields=['name']),
        ]
        constraints = [models.UniqueConstraint(fields=['restaurant', 'name'], name='unique_menu_item_per_restaurant')]

    def __str__(self):
        return f'{self.restaurant} - {self.name}'

# Create your models here.
