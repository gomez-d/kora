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