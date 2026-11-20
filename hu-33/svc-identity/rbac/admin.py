from django.contrib import admin

from .models import (
    Role,
    Permission,
    UserRole,
    RolePermission
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "id"
    )
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("id",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "resource",
        "action",
        "id"
    )
    search_fields = (
        "name",
        "resource",
        "action"
    )
    list_filter = (
        "resource",
        "action"
    )
    ordering = (
        "resource",
        "action"
    )
    readonly_fields = ("id",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "id"
    )
    search_fields = (
        "user__email",
        "role__name"
    )
    list_filter = ("role",)
    ordering = (
        "user__email",
        "role__name"
    )
    readonly_fields = ("id",)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = (
        "role",
        "permission",
        "id"
    )
    search_fields = (
        "role__name",
        "permission__name",
        "permission__resource",
        "permission__action"
    )
    list_filter = (
        "role",
        "permission__resource",
        "permission__action"
    )
    readonly_fields = ("id",)
