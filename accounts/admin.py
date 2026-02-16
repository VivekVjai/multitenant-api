from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Tenant & Role", {"fields": ("role", "tenant")}),
    )
