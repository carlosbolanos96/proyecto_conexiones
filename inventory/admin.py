from django.contrib import admin

from .models import InventoryItem


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'quantity', 'updated_at')
    search_fields = ('warehouse__name', 'product__name')
    raw_id_fields = ('warehouse', 'product')

# Register your models here.
