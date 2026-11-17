from django.urls import path

from rbac.views import (
    RoleView,
    RoleDetailView,
    PermissionView,
    PermissionDetailView,
    UserRoleView,
    UserRoleDetailView,
    RolePermissionView,
    RolePermissionDetailView,
    UserRolesQueryView
)

urlpatterns = [
    path(
        "roles/",
        RoleView.as_view(),
        name="roles"
    ),
    path(
        "roles/<uuid:role_id>/",
        RoleDetailView.as_view(),
        name="role-detail"
    ),

    path(
        "permissions/",
        PermissionView.as_view(),
        name="permissions"
    ),
    path(
        "permissions/<uuid:permission_id>/",
        PermissionDetailView.as_view(),
        name="permission-detail"
    ),

    path(
        "user-roles/",
        UserRoleView.as_view(),
        name="user-roles"
    ),
    path(
        "user-roles/<uuid:user_role_id>/",
        UserRoleDetailView.as_view(),
        name="user-role-detail"
    ),

    path(
        "role-permissions/",
        RolePermissionView.as_view(),
        name="role-permissions"
    ),
    path(
        "role-permissions/<uuid:role_permission_id>/",
        RolePermissionDetailView.as_view(),
        name="role-permission-detail"
    ),
    path(
        "users/<uuid:user_id>/roles/",
        UserRolesQueryView.as_view(),
        name="user-roles-query"
    ),
]
