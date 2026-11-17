from django.db import migrations

IDENTITY_PERMISSIONS = [
    {
        "name": "roles.read",
        "resource": "roles",
        "action": "read",
        "description": "Read system roles.",
    },
    {
        "name": "roles.create",
        "resource": "roles",
        "action": "create",
        "description": "Create system roles.",
    },
    {
        "name": "roles.update",
        "resource": "roles",
        "action": "update",
        "description": "Update system roles."
    },
    {
        "name": "roles.delete",
        "resource": "roles",
        "action": "delete",
        "description": "Delete system roles.",
    },
    {
        "name": "permissions.read",
        "resource": "permissions",
        "action": "read",
        "description": "Read system permissions."
    },
    {
        "name": "permissions.create",
        "resource": "permissions",
        "action": "create",
        "description": "Create system permissions."
    },
    {
        "name": "permissions.update",
        "resource": "permissions",
        "action": "update",
        "description": "Update system permissions."
    },
    {
        "name": "permissions.delete",
        "resource": "permissions",
        "action": "delete",
        "description": "Delete system permissions."
    },
    {
        "name": "user_roles.read_any",
        "resource": "user_roles",
        "action": "read_any",
        "description": "Read role assignments for any user."
    },
    {
        "name": "user_roles.assign",
        "resource": "user_roles",
        "action": "assign",
        "description": "Assign roles to users.",
    },
    {
        "name": "user_roles.remove",
        "resource": "user_roles",
        "action": "remove",
        "description": "Remove roles from users."
    },
    {
        "name": "role_permissions.read",
        "resource": "role_permissions",
        "action": "read",
        "description": "Read role-permission assignments.",
    },
    {
        "name": "role_permissions.assign",
        "resource": "role_permissions",
        "action": "assign",
        "description": "Assign permissions to roles.",
    },
    {
        "name": "role_permissions.remove",
        "resource": "role_permissions",
        "action": "remove",
        "description": "Remove permissions from roles.",
    },
]

def create_identity_permissions(apps, schema_editor):
    """
    Create identity RBAC permissions and assign them to the ADMIN role.
    """
    Role = apps.get_model("rbac", "Role")
    Permission = apps.get_model("rbac", "Permission")
    RolePermission = apps.get_model("rbac", "RolePermission")

    admin_role = Role.objects.get(name="ADMIN")

    for permission_data in IDENTITY_PERMISSIONS:
        permission, _ = Permission.objects.get_or_create(
            name=permission_data["name"],
            defaults={
                "resource": permission_data["resource"],
                "action": permission_data["action"],
                "description": permission_data["description"],
            },
        )

        RolePermission.objects.get_or_create(
            role=admin_role,
            permission=permission,
        )

def remove_identity_permissions(apps, schema_editor):
    """
    Remove the identity permissions introduced by this migration.
    """
    Permission = apps.get_model("rbac", "Permission")

    permission_names = [
        permission["name"]
        for permission in IDENTITY_PERMISSIONS
    ]

    Permission.objects.filter(
        name__in=permission_names
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("rbac", "0006_create_default_roles"),
    ]

    operations = [
        migrations.RunPython(
            create_identity_permissions,
            remove_identity_permissions,
        ),
    ]