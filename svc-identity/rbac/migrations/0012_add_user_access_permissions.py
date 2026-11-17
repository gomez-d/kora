from django.db import migrations


def create_user_access_permissions(apps, schema_editor):
    """
    Create user-resource permissions required by protected
    identity endpoints and assign them to the appropriate roles.
    """

    Permission = apps.get_model("rbac", "Permission")
    Role = apps.get_model("rbac", "Role")
    RolePermission = apps.get_model("rbac", "RolePermission")

    permissions = [
        {
            "name": "users.read_self",
            "resource": "users",
            "action": "read_self",
            "description": "Read the authenticated user's own information.",
            "roles": ["USER", "ADMIN"],
        },
        {
            "name": "users.update_self",
            "resource": "users",
            "action": "update_self",
            "description": "Update the authenticated user's own information.",
            "roles": ["USER", "ADMIN"],
        },
        {
            "name": "users.deactivate_self",
            "resource": "users",
            "action": "deactivate_self",
            "description": "Deactivate the authenticated user's own account.",
            "roles": ["USER", "ADMIN"],
        },
        {
            "name": "users.read_any",
            "resource": "users",
            "action": "read_any",
            "description": "Read information from any user account.",
            "roles": ["ADMIN"],
        },
        {
            "name": "users.deactivate_any",
            "resource": "users",
            "action": "deactivate_any",
            "description": "Deactivate any user account.",
            "roles": ["ADMIN"],
        },
    ]

    for permission_data in permissions:
        role_names = permission_data.pop("roles")

        permission, _ = Permission.objects.get_or_create(
            name=permission_data["name"],
            defaults={
                "resource": permission_data["resource"],
                "action": permission_data["action"],
                "description": permission_data["description"],
            },
        )

        for role_name in role_names:
            role = Role.objects.get(name=role_name)

            RolePermission.objects.get_or_create(
                role=role,
                permission=permission,
            )


def remove_user_access_permissions(apps, schema_editor):
    """
    Remove user-resource permissions created by this migration.
    """

    Permission = apps.get_model("rbac", "Permission")

    permission_names = [
        "users.read_self",
        "users.update_self",
        "users.deactivate_self",
        "users.read_any",
        "users.deactivate_any",
    ]

    Permission.objects.filter(
        name__in=permission_names
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rbac", "0011_add_consumption_update_permission"),
    ]

    operations = [
        migrations.RunPython(
            create_user_access_permissions,
            remove_user_access_permissions,
        ),
    ]