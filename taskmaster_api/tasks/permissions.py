from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # if request.method in permissions.SAFE_METHODS:
        # return True
        return obj.author == request.user


class IsProjectMemberForTask(permissions.BasePermission):
    """
    Custom permission to only allow members of a project to access its tasks.
    """

    def has_object_permission(self, request, view, obj):
        # return obj.project.members.filter(id=request.user.id).exists()
        task = obj

        # --- THIS IS THE NEW, ROBUST LOGIC ---
        if task.project:
            # Case 1: The task is part of a project.
            # Check if the user is a member of that project.
            return task.project.members.filter(id=request.user.id).exists()
        else:
            # Case 2: The task is a personal task (no project).
            # Check if the user is the author of the task.
            return task.author == request.user
