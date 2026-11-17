def get_user_role_names(user):
    """
    Return the role names currently assigned to a user.

    Role information is retrieved from the identity database and
    must not be provided by the client.
    """

    return list(
        user.roles.values_list(
            "name",
            flat=True
        )
    )

def get_user_permission_names(user):
    """
    Return the effective permission names granted to a user
    through their assigned roles.
    """
    return list(
        user.roles.filter(
            permissions__isnull=False
        ).values_list(
            "permissions__name",
            flat=True
        ).distinct()
    )