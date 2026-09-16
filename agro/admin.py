from django.contrib import admin

from .models import Producer, Product


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'tax_id', 'profile', 'address')
    search_fields = ('business_name', 'tax_id', 'profile__user__username')
    raw_id_fields = ('profile', 'address')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'producer', 'price', 'unit', 'is_active')
    list_filter = ('unit', 'is_active')
    search_fields = ('name', 'producer__business_name')
    raw_id_fields = ('producer',)

# Register your models here.
