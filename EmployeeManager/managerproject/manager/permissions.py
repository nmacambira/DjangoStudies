from rest_framework import permissions


class IsTaskOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow employee of an task to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            # DELETE permission are only allowed to the managers of an employee's task
            if request.method == 'DELETE':
                return obj.employee.manager == request.user or\
                       (request.user.is_staff and obj.employee == request.user)
            # UPDATE permissions are only allowed to the employee of a task or its manager
            return obj.employee == request.user or obj.employee.manager == request.user


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Global permission to only allow staff users to edit it.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        else:
            if request.method == 'DELETE':
                return False

            # WRITE permissions are only allowed to the manager of a project
            return request.user and request.user.is_staff
