from django.contrib import admin

from .models import RestaurantProduct


@admin.register(RestaurantProduct)
class RestaurantProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'restaurant__name')
    raw_id_fields = ('restaurant',)

# Register your models here.
