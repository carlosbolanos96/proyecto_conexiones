from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Payment(models.Model):
    """Simulated payment attached to one order."""

    class Method(models.TextChoices):
        CASH = 'cash', 'Efectivo'
        CARD = 'card', 'Tarjeta'
        TRANSFER = 'transfer', 'Transferencia'
        SIMULATED = 'simulated', 'Simulado'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
        REFUNDED = 'refunded', 'Reembolsado'

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment', verbose_name='pedido')
    method = models.CharField(max_length=30, choices=Method.choices, verbose_name='método')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='monto')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='estado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return f'Order #{self.order_id} - {self.status}'

# Create your models here.
