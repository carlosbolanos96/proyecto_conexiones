from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('restaurant_product', 'agro_product')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'consumer', 'mode', 'status', 'total', 'created_at')
    list_filter = ('mode', 'status', 'created_at')
    search_fields = ('consumer__username',)
    raw_id_fields = ('consumer', 'delivery_address')
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'restaurant_product', 'agro_product', 'quantity', 'unit_price')
    raw_id_fields = ('order', 'restaurant_product', 'agro_product')

# Register your models here.
