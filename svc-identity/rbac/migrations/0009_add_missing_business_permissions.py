from django.db import migrations

# Define the additional business permissions discovered after
# reviewing the current svc-business endpoints.

# Each permission includes:
# - name: unique RBAC identifier used by the permission classes.
# - resource: resource protected by the permission.
# - action: operation allowed over that resource.
# - description: human-readable explanation.
# - roles: roles that must receive the permission.

ADDITIONAL_BUSINESS_PERMISSIONS = [
    {
        "name": "food_categories.read",
        "resource": "food_categories",
        "action": "read",
        "description": "Read the shared food category catalog.",
        "roles": ["USER", "ADMIN"],
    },
    {
        "name": "consumptions.read_self",
        "resource": "consumptions",
        "action": "read_self",
        "description": (
            "Read consumption records that belong to the "
            "authenticated user."
        ),
        "roles": ["USER", "ADMIN"],
    },
]

def create_additional_business_permissions(apps, schema_editor):
    """
    Create the missing business permissions and assign them
    to the corresponding Kora roles.
    """

    # Historical models must be obtained through apps.get_model()
    # inside migrations instead of importing current application models.
    Role = apps.get_model("rbac", "Role")
    Permission = apps.get_model("rbac", "Permission")
    RolePermission = apps.get_model("rbac", "RolePermission")

    # Process each permission defined above.
    for permission_data in ADDITIONAL_BUSINESS_PERMISSIONS:

        # Create the permission only if it does not already exist.

        # get_or_create() makes the migration safe against
        # duplicate permission records.
        permission, _ = Permission.objects.get_or_create(
            name=permission_data["name"],
            defaults={
                "resource": permission_data["resource"],
                "action": permission_data["action"],
                "description": permission_data["description"],
            },
        )

        # Assign the permission to every role defined for it.
        for role_name in permission_data["roles"]:

            # Retrieve the existing USER or ADMIN role.
            role = Role.objects.get(name=role_name)

            # Create the role-permission association only if
            # it does not already exist.
            RolePermission.objects.get_or_create(
                role=role,
                permission=permission,
            )

def remove_additional_business_permissions(apps, schema_editor):
    """
    Remove the permissions introduced by this migration
    when the migration is rolled back.
    """

    Permission = apps.get_model("rbac", "Permission")

    # Extract only the permission names so they can be
    # removed in a single database query.
    permission_names = [
        permission["name"]
        for permission in ADDITIONAL_BUSINESS_PERMISSIONS
    ]

    # Deleting the Permission records also removes their
    # RolePermission associations through the database relations.
    Permission.objects.filter(
        name__in=permission_names
    ).delete()

class Migration(migrations.Migration):
    # This migration must run after the original business
    # permission migration because it complements that set.
    dependencies = [
        ("rbac", "0008_create_business_permissions"),
    ]

    operations = [
        migrations.RunPython(
            create_additional_business_permissions,
            remove_additional_business_permissions,
        ),
    ]