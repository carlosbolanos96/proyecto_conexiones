from django.contrib import admin

from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'owner__username', 'address__city')
    raw_id_fields = ('owner', 'address')

# Register your models here.
