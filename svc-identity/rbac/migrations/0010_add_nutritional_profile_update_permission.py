from django.db import migrations


def create_nutritional_profile_update_permission(apps, schema_editor):
    """
    Create the permission required to update a user's own
    nutritional profile and assign it to the standard Kora roles.
    """

    # Obtain historical versions of the RBAC models.
    Permission = apps.get_model("rbac", "Permission")
    Role = apps.get_model("rbac", "Role")
    RolePermission = apps.get_model("rbac", "RolePermission")

    # Create the self-scoped nutritional profile update permission.
    permission, _ = Permission.objects.get_or_create(
        name="nutritional_profiles.update_self",
        defaults={
            "resource": "nutritional_profiles",
            "action": "update_self",
            "description": (
                "Allows a user to update their own nutritional profile."
            ),
        },
    )

    # Both USER and ADMIN may modify their own nutritional profile.
    # ADMIN does not automatically receive access to profiles
    # belonging to other users.
    for role_name in ["USER", "ADMIN"]:
        role = Role.objects.get(name=role_name)

        RolePermission.objects.get_or_create(
            role=role,
            permission=permission,
        )


def remove_nutritional_profile_update_permission(apps, schema_editor):
    """
    Remove the self-scoped nutritional profile update permission.
    """

    Permission = apps.get_model("rbac", "Permission")

    Permission.objects.filter(
        name="nutritional_profiles.update_self"
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rbac", "0009_add_missing_business_permissions"),
    ]

    operations = [
        migrations.RunPython(
            create_nutritional_profile_update_permission,
            remove_nutritional_profile_update_permission,
        ),
    ]