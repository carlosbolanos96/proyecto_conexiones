from django.db import models


class Warehouse(models.Model):
    """Storage location owned by an agro producer."""

    producer = models.ForeignKey('agro.Producer', on_delete=models.CASCADE, related_name='warehouses', verbose_name='productor')
    name = models.CharField(max_length=120, verbose_name='nombre')
    address = models.ForeignKey('locations.Address', on_delete=models.PROTECT, related_name='warehouses', verbose_name='dirección')
    is_active = models.BooleanField(default=True, verbose_name='activa')

    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['name']
        indexes = [models.Index(fields=['producer'])]
        constraints = [models.UniqueConstraint(fields=['producer', 'name'], name='unique_warehouse_per_producer')]

    def __str__(self):
        return f'{self.producer} - {self.name}'

# Create your models here.
