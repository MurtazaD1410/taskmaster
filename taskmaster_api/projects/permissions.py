from rest_framework import permissions


class IsProjectOwner(permissions.BasePermission):
    """
    Custom permission to only allow the owner of a project to perform an action.
    """

    message = "You must be the project owner to perform this action."

    def has_object_permission(self, request, view, obj):
        # 'obj' will be the Project instance.
        # We check against the explicit 'owner' field on the Project model.
        return obj.owner == request.user


# You will also need a permission to check for general membership
class IsMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a project to view it.
    """

    message = "You must be a member of this project to view it."

    def has_object_permission(self, request, view, obj):
        # Check if a membership entry exists for this user and project.
        return obj.members.filter(id=request.user.id).exists()
