from rest_framework import permissions


class EstEditeurOuLectureSeule(permissions.BasePermission):
    """
    Permission personnalisée :
    - Accès en lecture (GET) accordé à tous les membres connectés.
    - Accès en écriture (POST, PUT, DELETE) réservé aux éditeurs (is_staff).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff