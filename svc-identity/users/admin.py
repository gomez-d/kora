from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, RefreshToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "is_active",
        "is_staff"
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {
            "fields": ("first_name", "last_name", "date_of_birth")
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions"
            )
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined")
        })
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "first_name",
                "last_name",
                "date_of_birth",
                "password1",
                "password2",
                "is_staff",
                "is_superuser"
            )
        }),
    )


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "token_jti",
        "expires_at",
        "revoked_at",
        "created_at",
        "id"
    )
    search_fields = (
        "user__email",
        "token_jti"
    )
    list_filter = (
        "expires_at",
        "revoked_at",
        "created_at"
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "created_at"
    )
