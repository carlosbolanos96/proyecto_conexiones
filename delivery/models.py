from django.core.exceptions import ValidationError
from django.db import models


class Courier(models.Model):
    """Courier availability and vehicle data."""

    class Vehicle(models.TextChoices):
        BIKE = 'bike', 'Bicicleta'
        MOTORCYCLE = 'motorcycle', 'Motocicleta'
        CAR = 'car', 'Auto'
        VAN = 'van', 'Camioneta'

    profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE, related_name='courier', verbose_name='perfil')
    vehicle_type = models.CharField(max_length=20, choices=Vehicle.choices, verbose_name='tipo de vehículo')
    license_plate = models.CharField(max_length=20, blank=True, verbose_name='patente')
    is_available = models.BooleanField(default=False, verbose_name='disponible')
    service_area = models.CharField(max_length=150, blank=True, verbose_name='zona de servicio')

    class Meta:
        verbose_name = 'Transportador'
        verbose_name_plural = 'Transportadores'
        ordering = ['profile__user__username']
        indexes = [models.Index(fields=['is_available'])]

    def clean(self):
        super().clean()
        if self.profile_id and self.profile.role != 'courier':
            raise ValidationError({'profile': 'Courier profile must have courier role.'})

    def __str__(self):
        return f'{self.profile.user.username} ({self.vehicle_type})'


class Delivery(models.Model):
    """Delivery lifecycle for restaurant orders."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PICKED_UP = 'picked_up', 'Retirado'
        IN_TRANSIT = 'in_transit', 'En tránsito'
        DELIVERED = 'delivered', 'Entregado'

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='delivery', verbose_name='pedido')
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', verbose_name='transportador')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='estado')
    picked_at = models.DateTimeField(null=True, blank=True, verbose_name='fecha de retiro')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='fecha de entrega')

    class Meta:
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
        ordering = ['-id']
        indexes = [models.Index(fields=['status'])]

    def clean(self):
        super().clean()
        if self.order_id and self.order.mode != 'restaurant':
            raise ValidationError({'order': 'Deliveries are only available for restaurant orders.'})

    def __str__(self):
        return f'Delivery for order #{self.order_id}'

# Create your models here.
