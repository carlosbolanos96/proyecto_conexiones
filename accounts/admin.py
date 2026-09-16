from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'default_address')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')
    raw_id_fields = ('user', 'default_address')

# Register your models here.
