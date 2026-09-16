from django.contrib import admin

from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'producer', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'producer__business_name', 'address__city')
    raw_id_fields = ('producer', 'address')

# Register your models here.
