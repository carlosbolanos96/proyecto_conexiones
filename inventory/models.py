from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class InventoryItem(models.Model):
    """Stock quantity for one agro product in one warehouse."""

    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE, related_name='inventory_items', verbose_name='bodega')
    product = models.ForeignKey('agro.Product', on_delete=models.CASCADE, related_name='inventory_items', verbose_name='producto')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], verbose_name='cantidad')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='fecha de actualización')

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        ordering = ['warehouse__name', 'product__name']
        indexes = [
            models.Index(fields=['warehouse']),
            models.Index(fields=['product']),
        ]
        constraints = [models.UniqueConstraint(fields=['warehouse', 'product'], name='unique_product_per_warehouse')]

    def clean(self):
        super().clean()
        if self.warehouse_id and self.product_id and self.warehouse.producer_id != self.product.producer_id:
            raise ValidationError({'product': 'Product must belong to the same producer as the warehouse.'})

    def __str__(self):
        return f'{self.warehouse} - {self.product}: {self.quantity}'

# Create your models here.
