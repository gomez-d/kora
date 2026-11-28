
from django.db import migrations


def create_food_recognition_permission(apps, schema_editor):
    Permission = apps.get_model("rbac", "Permission")
    Role = apps.get_model("rbac", "Role")
    RolePermission = apps.get_model("rbac", "RolePermission")

    permission, _ = Permission.objects.get_or_create(
        name="food_recognition.create_self",
        defaults={
            "resource": "food_recognition",
            "action": "create_self",
            "description": (
                "Request food recognition using an image "
                "for the authenticated user."
            ),
        },
    )

    for role_name in ["USER", "ADMIN"]:
        role = Role.objects.get(name=role_name)

        RolePermission.objects.get_or_create(
            role=role,
            permission=permission,
        )


def remove_food_recognition_permission(apps, schema_editor):
    Permission = apps.get_model("rbac", "Permission")

    Permission.objects.filter(
        name="food_recognition.create_self"
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rbac", "0012_add_user_access_permissions"),
    ]

    operations = [
        migrations.RunPython(
            create_food_recognition_permission,
            remove_food_recognition_permission,
        ),
    ]
