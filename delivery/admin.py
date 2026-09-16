from django.contrib import admin

from .models import Courier, Delivery


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('profile', 'vehicle_type', 'license_plate', 'is_available', 'service_area')
    list_filter = ('vehicle_type', 'is_available')
    search_fields = ('profile__user__username', 'license_plate', 'service_area')
    raw_id_fields = ('profile',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'courier', 'status', 'picked_at', 'delivered_at')
    list_filter = ('status',)
    raw_id_fields = ('order', 'courier')

# Register your models here.
