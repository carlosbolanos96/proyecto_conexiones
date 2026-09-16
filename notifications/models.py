from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Message addressed to a user for simulated platform events."""

    class Type(models.TextChoices):
        ORDER = 'order', 'Pedido'
        PAYMENT = 'payment', 'Pago'
        DELIVERY = 'delivery', 'Entrega'
        SYSTEM = 'system', 'Sistema'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name='usuario')
    type = models.CharField(max_length=30, choices=Type.choices, verbose_name='tipo')
    message = models.TextField(verbose_name='mensaje')
    is_read = models.BooleanField(default=False, verbose_name='leído')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.type} - {self.user}'

# Create your models here.
