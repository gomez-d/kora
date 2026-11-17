from django.db import migrations


def create_consumption_update_permission(apps, schema_editor):
    """
    Create the permission required to update a user's own
    consumption records and assign it to the standard Kora roles.
    """

    # Obtain the historical RBAC models used by this migration.
    Permission = apps.get_model("rbac", "Permission")
    Role = apps.get_model("rbac", "Role")
    RolePermission = apps.get_model("rbac", "RolePermission")

    # Create the self-scoped permission used to modify
    # consumption records owned by the authenticated user.
    permission, _ = Permission.objects.get_or_create(
        name="consumptions.update_self",
        defaults={
            "resource": "consumptions",
            "action": "update_self",
            "description": (
                "Allows a user to update their own consumption records."
            ),
        },
    )

    # USER and ADMIN may modify only their own consumption records.
    # This permission does not grant access to records owned
    # by another user.
    for role_name in ["USER", "ADMIN"]:
        role = Role.objects.get(name=role_name)

        RolePermission.objects.get_or_create(
            role=role,
            permission=permission,
        )


def remove_consumption_update_permission(apps, schema_editor):
    """
    Remove the self-scoped consumption update permission.
    """

    Permission = apps.get_model("rbac", "Permission")

    Permission.objects.filter(
        name="consumptions.update_self"
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rbac", "0010_add_nutritional_profile_update_permission"),
    ]

    operations = [
        migrations.RunPython(
            create_consumption_update_permission,
            remove_consumption_update_permission,
        ),
    ]