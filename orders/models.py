from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    """Shared order for restaurant and agro purchases."""

    class Mode(models.TextChoices):
        RESTAURANT = 'restaurant', 'Restaurante'
        AGRO = 'agro', 'Agro'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        CONFIRMED = 'confirmed', 'Confirmado'
        IN_DELIVERY = 'in_delivery', 'En entrega'
        DELIVERED = 'delivered', 'Entregado'
        CANCELLED = 'cancelled', 'Cancelado'

    consumer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders', verbose_name='consumidor')
    mode = models.CharField(max_length=20, choices=Mode.choices, verbose_name='modo')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='estado')
    delivery_address = models.ForeignKey('locations.Address', on_delete=models.PROTECT, related_name='orders', verbose_name='dirección de entrega')
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], verbose_name='total')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='fecha de actualización')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['consumer']),
            models.Index(fields=['status']),
            models.Index(fields=['mode']),
            models.Index(fields=['created_at']),
        ]

    def clean(self):
        super().clean()
        if self.delivery_address_id and self.delivery_address.owner_id != self.consumer_id:
            raise ValidationError({'delivery_address': 'Delivery address must belong to the consumer.'})

    def __str__(self):
        return f'Order #{self.pk} - {self.mode} - {self.status}'


class OrderItem(models.Model):
    """Line item pointing to exactly one mode-specific product."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='pedido')
    restaurant_product = models.ForeignKey(
        'menus.RestaurantProduct',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='plato',
    )
    agro_product = models.ForeignKey(
        'agro.Product',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='producto agro',
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='cantidad')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='precio unitario')

    class Meta:
        verbose_name = 'Ítem del pedido'
        verbose_name_plural = 'Ítems del pedido'
        ordering = ['id']
        indexes = [models.Index(fields=['order'])]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(restaurant_product__isnull=False, agro_product__isnull=True)
                    | models.Q(restaurant_product__isnull=True, agro_product__isnull=False)
                ),
                name='exactly_one_order_item_product',
            ),
        ]

    def clean(self):
        super().clean()
        has_restaurant_product = self.restaurant_product_id is not None
        has_agro_product = self.agro_product_id is not None

        if has_restaurant_product == has_agro_product:
            raise ValidationError('Order item must reference exactly one product.')

        if self.order_id:
            if self.order.mode == Order.Mode.RESTAURANT and not has_restaurant_product:
                raise ValidationError({'restaurant_product': 'Restaurant orders require a restaurant product.'})
            if self.order.mode == Order.Mode.AGRO and not has_agro_product:
                raise ValidationError({'agro_product': 'Agro orders require an agro product.'})

    def __str__(self):
        product = self.restaurant_product or self.agro_product
        return f'Order #{self.order_id} - {product}'

# Create your models here.
