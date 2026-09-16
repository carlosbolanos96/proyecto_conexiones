from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'number', 'city', 'province', 'owner', 'is_default')
    list_filter = ('province', 'city', 'is_default')
    search_fields = ('street', 'number', 'city', 'province', 'owner__username')
    raw_id_fields = ('owner',)

# Register your models here.
