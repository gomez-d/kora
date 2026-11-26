from django.db import migrations


BUSINESS_PERMISSIONS = [
    {
        "name": "foods.read",
        "resource": "foods",
        "action": "read",
        "description": "Read the shared food catalog.",
        "roles": ["USER", "ADMIN"],
    },
    {
        "name": "foods.create",
        "resource": "foods",
        "action": "create",
        "description": "Create foods in the shared catalog.",
        "roles": ["ADMIN"],
    },
    {
        "name": "foods.update",
        "resource": "foods",
        "action": "update",
        "description": "Update foods in the shared catalog.",
        "roles": ["ADMIN"],
    },
    {
        "name": "foods.delete",
        "resource": "foods",
        "action": "delete",
        "description": "Delete foods from the shared catalog.",
        "roles": ["ADMIN"],
    },
    {
        "name": "food_categories.create",
        "resource": "food_categories",
        "action": "create",
        "description": "Create food categories.",
        "roles": ["ADMIN"],
    },
    {
        "name": "nutritional_profiles.read_self",
        "resource": "nutritional_profiles",
        "action": "read_self",
        "description": "Read the authenticated user's nutritional profile.",
        "roles": ["USER", "ADMIN"],
    },
    {
        "name": "nutritional_profiles.create_self",
        "resource": "nutritional_profiles",
        "action": "create_self",
        "description": "Create the authenticated user's nutritional profile.",
        "roles": ["USER", "ADMIN"],
    },
    {
        "name": "consumptions.create_self",
        "resource": "consumptions",
        "action": "create_self",
        "description": "Create consumption records for the authenticated user.",
        "roles": ["USER", "ADMIN"],
    },
]


def create_business_permissions(apps, schema_editor):
    """
    Create business permissions and assign them to the appropriate roles.
    """
    Role = apps.get_model("rbac", "Role")
    Permission = apps.get_model("rbac", "Permission")
    RolePermission = apps.get_model("rbac", "RolePermission")

    for permission_data in BUSINESS_PERMISSIONS:
        permission, _ = Permission.objects.get_or_create(
            name=permission_data["name"],
            defaults={
                "resource": permission_data["resource"],
                "action": permission_data["action"],
                "description": permission_data["description"],
            },
        )

        for role_name in permission_data["roles"]:
            role = Role.objects.get(name=role_name)

            RolePermission.objects.get_or_create(
                role=role,
                permission=permission,
            )


def remove_business_permissions(apps, schema_editor):
    """
    Remove the business permissions introduced by this migration.
    """
    Permission = apps.get_model("rbac", "Permission")

    permission_names = [
        permission["name"]
        for permission in BUSINESS_PERMISSIONS
    ]

    Permission.objects.filter(
        name__in=permission_names
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rbac", "0007_create_identity_permissions"),
    ]

    operations = [
        migrations.RunPython(
            create_business_permissions,
            remove_business_permissions,
        ),
    ]